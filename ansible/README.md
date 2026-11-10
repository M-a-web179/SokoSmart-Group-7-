# Deploy SokoSmart with Ansible

The playbook installs Docker, runs the price service, restricts incoming traffic
and disables root and password SSH login. It expects a dedicated Ubuntu server
with systemd, a sudo user and working SSH key access. Terraform provisions AWS;
Ansible configures the server afterwards. Do not run this on a shared server.

## Prepare the controller and server

Install Ansible and the pinned collections:

```sh
python3 -m venv ~/.venvs/sokosmart-ansible
~/.venvs/sokosmart-ansible/bin/pip install ansible ansible-lint==26.11.0
export PATH="$HOME/.venvs/sokosmart-ansible/bin:$PATH"
ansible-galaxy collection install -r ansible/requirements.yml
```

Follow ../terraform/README.md to provision the AWS server. Check the budget first.
From terraform/, obtain `terraform output -raw instance_public_ip` and
`terraform output -raw ssh_user`. Put those values into a copy of
inventory.ini.example called inventory.ini. Use the private key corresponding to
the public key configured in Terraform. Alternatively, from the repo root run `python3 ansible/inventory_from_terraform.py --key ~/.ssh/sokosmart_f3` to write the ignored static inventory from existing Terraform outputs. This reads state; it does not create or destroy resources. Verify the server's SSH fingerprint
before accepting it. Host key checking stays enabled.

From ansible/, copy local.yml.example to local.yml and replace its example CIDR
with your public IP followed by /32. Match Terraform's SSH rule. The inventory,
local.yml, private keys and Terraform state must stay out of Git.

## Choose how to deliver the image

For a published image, set app_image in local.yml to the team's image reference.
Prefer an immutable digest. For a private registry, authenticate on the server
privately first. This PR does not publish an image or store registry credentials.

You can also build this repo's Dockerfile and transfer a saved image over SSH:

```sh
# Run from the repository root. Match the target architecture.
docker build --platform linux/amd64 -t sokosmart-price:YOUR_COMMIT .
docker save -o /tmp/sokosmart-image.tar sokosmart-price:YOUR_COMMIT
```

Set app_image to that exact tag and app_image_archive to the absolute path of
the archive on your controller. For an ARM server or Apple Silicon local lab,
build with linux/arm64 instead. No registry upload is required in this mode.
Use a new commit tag for each build. The archive is loaded when it changes or
when the image is missing; it is not reloaded on every run.

Default ports are 5000 on the server and container, with /health as the health
endpoint. Runtime variables are in group_vars/all.yml and can be overridden in
local.yml. Keep secret values in the ignored file or use Ansible Vault. The
container task uses no_log so environment values do not appear in output.

## Run and verify

```sh
cd ansible
ansible app -m ping -e @local.yml
ansible-playbook site.yml -e @local.yml
ansible-playbook site.yml -e @local.yml
```

The second run should report changed=0. Package state, templates, services and
container settings are compared with the desired state. Handlers restart
services only after changes. Health requests are read-only. A changed image or
configuration should cause a change; do not hide real changes just to get zero.

From your laptop, run `curl -i http://SERVER_IP:5000/health` and check for HTTP
200. `/api/prices` should return the seeded crop prices. The app currently stores
new reports in memory, so they do not survive a container replacement. Persistent
PostgreSQL storage is separate work.

SSH hardening requires an existing authorized_keys file, validates with sshd -t,
and then restarts SSH through a handler. Root, password and keyboard-interactive
login are disabled. Do not remove your authorized key.

UFW allows SSH from the configured CIDR and the app port. Docker's published
ports can bypass UFW's INPUT rules, so a systemd service also applies a
DOCKER-USER forwarding policy. It preserves established and container-originated
traffic, allows the app port and blocks other inbound forwarded traffic. This
requires Docker's iptables backend and is intended for a dedicated app server.
See https://docs.docker.com/engine/network/packet-filtering-firewalls/.

## Local verification without AWS charges

The tests/Dockerfile is an Ubuntu/systemd SSH fixture for local Docker only.
It requires a privileged container with a writable cgroup mount and must never
be exposed publicly or used as a production server. Build it with SSH_USER and
your public SSH key as SSH_PUBKEY. Never pass a private key as a build argument.
Forward SSH and app ports on 127.0.0.1 only. Set ansible_port to the forwarded
SSH port and ssh_allowed_cidr to the Docker gateway address /32 as seen by the
server. Nested Docker uses vfs; EC2 retains Docker's normal storage defaults.
This verifies configuration but does not prove AWS provisioning.

## Lint and cleanup

From the repo root, run:

```sh
ansible-lint ansible/site.yml ansible/playbook.yml ansible/roles
```

The Ansible workflow runs the same check on pull requests. Local verification
logs are in ../evidence/domyusuf and the explanation is in ../team-notes.md.

For AWS, use terraform destroy from terraform/ and verify the EC2 resources are
gone. For the local fixture, remove the inner app container and image, then the
outer Ubuntu container and fixture image. Save cleanup output as evidence.
Do not destroy a teammate's server or shared state. Dynamic cloud inventory,
fail2ban and unattended upgrades are possible follow-up improvements.
