#!/usr/bin/env python3
"""Generate ignored inventory and deployment settings from existing Terraform outputs."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess


ECR_URL = re.compile(
    r"(?P<registry>(?P<account>\d{12})\.dkr\.ecr\."
    r"(?P<region>[a-z0-9-]+)\.amazonaws\.com(?:\.cn)?)/[a-z0-9][a-z0-9._/-]*"
)


def deployment_files(outputs, key, image_tag):
    """Return public connection metadata, never the contents of a database secret."""
    if not re.fullmatch(r"[A-Za-z0-9_./~-]+", key):
        raise ValueError("Use a key path without spaces or shell metacharacters.")
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}", image_tag):
        raise ValueError("Use the exact published Docker image tag.")
    bastion = str(ipaddress.IPv4Address(outputs["bastion_public_ip"]["value"]))
    app = str(ipaddress.IPv4Address(outputs["app_private_ip"]["value"]))
    user = outputs["ssh_user"]["value"]
    if user != "ubuntu":
        raise ValueError("Expected the Ubuntu deployment user; check Terraform outputs.")
    repository = outputs["ecr_repository_url"]["value"]
    match = ECR_URL.fullmatch(repository)
    if not match:
        raise ValueError("ecr_repository_url must be a private AWS ECR repository URL.")
    secret_arn = outputs["db_secret_arn"]["value"]
    arn = secret_arn.split(":", 5)
    if (len(arn) != 6 or arn[0] != "arn" or arn[2] != "secretsmanager"
            or arn[3] != match["region"] or arn[4] != match["account"]
            or not arn[5].startswith("secret:")):
        raise ValueError("Use the database secret and ECR outputs from the same AWS stack.")
    jump = (f'-o ProxyCommand="ssh -i {key} -W %h:%p '
            f'-o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes {user}@{bastion}"')
    inventory = (
        "[bastion]\n"
        f"bastion_host ansible_host={bastion} "
        "ansible_ssh_common_args='-o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes'\n"
        "\n[app]\n"
        f"app_host ansible_host={app} "
        f"ansible_ssh_common_args='{jump} -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes'\n"
        "\n[all:vars]\n"
        f"ansible_user={user}\n"
        f"ansible_ssh_private_key_file={key}\n"
        "ansible_python_interpreter=/usr/bin/python3\n"
    )
    settings = {
        "aws_region": match["region"],
        "ecr_registry": match["registry"],
        "app_image": f"{repository}:{image_tag}",
        "db_secret_arn": secret_arn,
    }
    return inventory, settings


def write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)
    path.chmod(0o600)


def read_outputs(path):
    raw = Path(path).read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return json.loads(raw.decode(encoding))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True, help="Your private SSH key on the Ansible controller")
    parser.add_argument("--image-tag", required=True, help="An existing immutable ECR image tag")
    parser.add_argument("--outputs", help="JSON export from Terraform (UTF-8 or Windows UTF-16)")
    parser.add_argument("--force", action="store_true", help="Replace generated files; never changes local.yml")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        key = str(Path(args.key).expanduser().resolve(strict=True))
        if args.outputs:
            outputs = read_outputs(args.outputs)
        else:
            outputs = json.loads(subprocess.check_output(
                ["terraform", f"-chdir={root / 'terraform'}", "output", "-json"],
                text=True,
            ))
        inventory, settings = deployment_files(outputs, key, args.image_tag)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Cannot generate deployment files: {error}\n")
    inventory_path = root / "ansible" / "inventory.ini"
    settings_path = root / "ansible" / "terraform.generated.yml"
    if not args.force and any(path.exists() for path in (inventory_path, settings_path)):
        parser.exit(1, "Generated files already exist. Check them first, then use --force to replace them.\n")
    write_private(inventory_path, inventory)
    write_private(settings_path, json.dumps(settings, indent=2) + "\n")
    print(f"Wrote {inventory_path} and {settings_path}. local.yml was not changed.")
    print("Verify both server fingerprints with M-a-web179 before connecting.")


if __name__ == "__main__":
    main()
