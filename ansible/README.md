# Deploy SokoSmart through the bastion

Terraform creates the AWS network, bastion, private Ubuntu app server, ECR
repository and RDS database. Ansible connects through the bastion, installs Docker
Compose, pulls the image using the app VM's IAM role, reads the database secret,
and configures nginx on the bastion. Use the dedicated project servers only.

## Before connecting

Ask M-a-web179 to confirm the stack is applied, the budget alert is active, and
which immutable image tag exists in ECR. Each person uses their own SSH key.
Your public key must be authorized on both servers and your public IP allowed by
the bastion security group. Never send a private key, AWS access key or database
password through chat or commit one to Git. Agree who owns teardown before testing.

The controller can be Ubuntu, WSL Ubuntu or macOS. Install the tools:

```sh
python3 -m venv ~/.venvs/sokosmart-ansible
. ~/.venvs/sokosmart-ansible/bin/activate
pip install ansible ansible-lint==26.11.0
ansible-galaxy collection install -r ansible/requirements.yml
```

Run these from the repo root. A current Ansible release avoids the unsupported
2.16 collection warnings in the older deployment log. Check the bastion and app
SSH fingerprints with M-a-web179 before first use. Generated inventory uses
accept-new to record first connections and refuses changed host keys. It uses
an SSH ProxyCommand with your key to implement the bastion jump without agent
forwarding or copying the private key to the bastion.

## Generate inventory and deployment settings

Use outputs from the existing Terraform state, not a fresh apply:

```sh
python3 ansible/inventory_from_terraform.py \
  --key ~/.ssh/sokosmart_f3 \
  --image-tag YOUR_PUBLISHED_COMMIT_TAG
```

If Terraform runs in PowerShell and Ansible runs in WSL, export outputs on the
Terraform controller first:

```sh
terraform -chdir=terraform output -json > terraform/outputs.json
python3 ansible/inventory_from_terraform.py \
  --outputs terraform/outputs.json \
  --key ~/.ssh/sokosmart_f3 \
  --image-tag YOUR_PUBLISHED_COMMIT_TAG
```

Use the private key's WSL path, not a Windows drive path. The helper accepts
UTF-8 JSON with or without a BOM, and Windows PowerShell UTF-16 exports. It reads bastion_public_ip,
app_private_ip, ssh_user, ecr_repository_url and db_secret_arn. The registry,
region, secret ARN and complete image reference come from those outputs; no
account ID is hardcoded. Your selected tag must already exist in ECR. The helper
never fetches a secret's value, creates infrastructure or publishes an image.

It writes ignored, mode-0600 files ansible/inventory.ini and
ansible/terraform.generated.yml. Existing files are preserved unless --force is
specified. Inspect them before regenerating after an AWS rebuild. local.yml is
never overwritten. Output exports may contain sensitive Terraform outputs; keep
terraform/outputs.json private and delete it after use.

Copy ansible/local.yml.example to ansible/local.yml for optional overrides. The
standard ECR deployment needs none. Do not override the registry with another
account's value. For deliberate local image delivery, set app_image to the saved
tag and app_image_archive to an absolute controller-side docker save archive.
Build for linux/amd64 for the Terraform app VM. This fallback still uses the
real database secret and does not replace AWS verification.

## Deploy the app and proxy

```sh
cd ansible
ansible all -m ping -e @terraform.generated.yml -e @local.yml
ansible-playbook site.yml -e @terraform.generated.yml -e @local.yml
ansible-playbook site.yml -e @terraform.generated.yml -e @local.yml
```

site.yml configures the private app first, then imports proxy.yml to configure
nginx on the bastion. playbook.yml is an equivalent wrapper. To update only the
proxy later, run `ansible-playbook proxy.yml` with the same two extra-vars files.

The app role installs amazon-ecr-credential-helper and writes a separate Docker
configuration under /opt/sokosmart/docker. Docker uses that helper with the VM
instance profile when pulling. No manual docker login or static AWS credential
is needed. The helper obtains renewable ECR credentials without a token-writing
Ansible task reporting a change on each run. Existing global Docker login settings
are not overwritten. The app VM must be able to reach ECR, Secrets Manager, S3
image layers and Ubuntu package mirrors through the configured NAT gateway.

The database URL is fetched on the app VM and written to root-only
/opt/sokosmart/app.env with sslmode=require. Secret tasks use no_log. The secret
reference and registry come from Terraform; passwords stay out of inventory and
controller settings. Do not print app.env, Docker environment dumps or secret
values while collecting evidence.

The second identical run should report changed=0 for both app and bastion.
Packages, files, services and Compose state are compared with the desired state;
handlers only reload services when configuration changes. Token lookup is handled
by Docker's credential helper. A new image, secret rotation or configuration edit
should still report genuine changes. Do not hide those changes just to get zero.

## Verify from outside AWS

Replace BASTION_PUBLIC_IP with the Terraform output:

```sh
curl --fail --show-error -i http://BASTION_PUBLIC_IP/health
curl --fail --show-error -i http://BASTION_PUBLIC_IP/ready
curl --fail --show-error http://BASTION_PUBLIC_IP/api/prices
```

/health is process liveness only. The deployment and Compose health checks use
/ready and require checks.database to equal ok; HTTP 200 with not_configured is
also rejected. The proxy role checks the same response through nginx. A broken
RDS connection must fail deployment even if /health still answers successfully.
The outside-AWS curl confirms public ingress separately from checks on the servers.

Database connectivity is checked with SELECT 1. Price reports still use the
application's in-memory repository, so a ready database does not prove report
persistence. Newly added reports can be lost when the container is recreated.

## Runbook

Connect with your key; the second command uses the bastion as a jump host:

```sh
ssh -i ~/.ssh/sokosmart_f3 ubuntu@BASTION_PUBLIC_IP
ssh -o 'ProxyCommand=ssh -i ~/.ssh/sokosmart_f3 -W %h:%p ubuntu@BASTION_PUBLIC_IP' \
  -i ~/.ssh/sokosmart_f3 ubuntu@APP_PRIVATE_IP
```

On the app VM, use this prefix for Compose commands:

```sh
sudo env DOCKER_CONFIG=/opt/sokosmart/docker \
  docker compose -p sokosmart-price -f /opt/sokosmart/docker-compose.yml ps
sudo env DOCKER_CONFIG=/opt/sokosmart/docker \
  docker compose -p sokosmart-price -f /opt/sokosmart/docker-compose.yml logs --tail=100 app
curl --fail --show-error http://127.0.0.1:5000/ready
```

Review logs privately before saving them. Do not include compose config output,
app.env, docker inspect environment values or AWS secret responses in evidence.
On the bastion, use `sudo nginx -t`, `sudo systemctl status nginx --no-pager` and
`curl --fail http://127.0.0.1/ready` to check the proxy.

If /health succeeds but /ready fails, check the RDS status, secret reference,
app-to-database security group rule, NAT connectivity and IAM permission to read
the secret. If the app is ready locally but the public URL fails, check nginx,
the bastion-to-app rule and public HTTP ingress. Do not open SSH or PostgreSQL to
the world to troubleshoot. UFW restricts app SSH to the bastion private IP, and
DOCKER-USER filters published Docker ports as well as the host firewall.

For a failed image deployment, select a known-good immutable tag that still exists
in ECR. Regenerate settings with --image-tag PREVIOUS_TAG --force, then rerun the
same site.yml command. This is a manual rollback; the playbook does not
automatically restore an older image after a readiness failure. Database schema
or credential changes may need separate recovery. Confirm /ready and the public
API after rollback, then repeat the successful deployment to confirm changed=0.

## Checks and remaining AWS evidence

From the repo root:

```sh
ansible-lint ansible/site.yml ansible/playbook.yml ansible/proxy.yml ansible/roles
python3 -m unittest discover -s ansible/tests -p 'test_*.py'
```

The automated tests check configuration generation and reject missing or broken
database readiness using a local HTTP stub. They do not provision AWS, authenticate
to ECR or prove a cloud run is idempotent.

The older first-run AWS logs and curl results are in evidence/summative. They do
not verify these follow-up changes. Still to test with M-a-web179:

- Run the updated playbook against both real servers, then save the second
  unchanged run showing changed=0, failed=0 and unreachable=0 for both hosts.
- Pull an image missing from the VM through the IAM-backed ECR helper, then
  exercise another pull after token renewal. No long-lived AWS keys should be used.
- Verify /ready reports database=ok internally and through the public bastion.
  In a disposable test, verify an unavailable DB causes deployment to fail;
  restore connectivity afterwards. Do not rotate the shared DB password casually.
- Verify SSH access through the bastion, root-only secret-file permissions,
  the Docker forwarding policy and nginx configuration on the actual hosts.
- Practice rollback to an existing earlier image tag and verify readiness again.
- Agree who runs terraform destroy, capture cleanup proof and check AWS for
  remaining billable resources. Do not destroy a teammate's live server or shared
  Terraform state without agreement.

Save evidence with GitHub usernames and explicit filenames. Redact sensitive
values; never commit keys, local.yml, generated inventory/settings, Terraform
state or saved plan files.
