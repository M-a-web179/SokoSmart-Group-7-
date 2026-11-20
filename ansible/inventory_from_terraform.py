#!/usr/bin/env python3
"""Write ignored static inventory (bastion plus app VM behind it) from Terraform outputs; no apply."""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--key', required=True, help='Path to the private SSH key as seen by Ansible')
parser.add_argument('--outputs', help='JSON file from terraform output -json; if omitted, terraform is run')
args = parser.parse_args()

if not re.fullmatch(r'[A-Za-z0-9_./~-]+', args.key):
    raise SystemExit('Key path may only contain letters, digits and _ . / ~ -')

root = Path(__file__).resolve().parents[1]
if args.outputs:
    outputs = json.loads(Path(args.outputs).read_text(encoding='utf-8-sig'))
else:
    outputs = json.loads(subprocess.check_output(
        ['terraform', f'-chdir={root / "terraform"}', 'output', '-json'], text=True
    ))

bastion = str(ipaddress.ip_address(outputs['bastion_public_ip']['value']))
app = str(ipaddress.ip_address(outputs['app_private_ip']['value']))
user = outputs['ssh_user']['value']
if user != 'ubuntu':
    raise SystemExit('Expected the Ubuntu deployment user; check Terraform outputs.')

jump = (f'-o ProxyCommand="ssh -i {args.key} -W %h:%p '
        f'-o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes {user}@{bastion}"')
text = (
    '[bastion]\n'
    f"bastion ansible_host={bastion} ansible_ssh_common_args='-o StrictHostKeyChecking=accept-new'\n"
    '\n[app]\n'
    f"app ansible_host={app} ansible_ssh_common_args='{jump} -o StrictHostKeyChecking=accept-new'\n"
    '\n[all:vars]\n'
    f'ansible_user={user}\n'
    f'ansible_ssh_private_key_file={args.key}\n'
    'ansible_python_interpreter=/usr/bin/python3\n'
)
path = root / 'ansible' / 'inventory.ini'
path.write_text(text)
path.chmod(0o600)
print(f'Wrote {path}.')