#!/usr/bin/env python3
"""Write ignored static inventory from existing Terraform outputs; no apply."""
import argparse
import ipaddress
import json
from pathlib import Path
import shlex
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--key', required=True, help='Path to your private SSH key')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
outputs = json.loads(subprocess.check_output(
    ['terraform', f'-chdir={root / "terraform"}', 'output', '-json'], text=True
))
host = str(ipaddress.ip_address(outputs['instance_public_ip']['value']))
user = outputs['ssh_user']['value']
if user != 'ubuntu':
    raise SystemExit('Expected the Ubuntu deployment user; check Terraform outputs.')
key = Path(args.key).expanduser().resolve(strict=True)
line = (f'sokosmart ansible_host={host} ansible_user={user} '
        f'ansible_ssh_private_key_file={shlex.quote(str(key))}\n')
path = root / 'ansible' / 'inventory.ini'
path.write_text('[app]\n' + line + '\n[app:vars]\n'
                'ansible_python_interpreter=/usr/bin/python3\n')
path.chmod(0o600)
print(f'Wrote {path}. Verify the SSH fingerprint before connecting.')
