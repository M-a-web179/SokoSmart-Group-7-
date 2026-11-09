# SokoSmart infrastructure (Terraform)

Terraform for Formative 3, Part 1. It builds one Ubuntu server on AWS for the
price-service, which Ansible (Part 2) then configures.

```
Internet
   │
   ▼
Internet gateway ── route table (0.0.0.0/0)
   │
VPC 10.20.0.0/16
 ├─ public subnet eu-west-1a 10.20.0.0/24 ── EC2 t3.micro (Ubuntu 24.04)
 └─ public subnet eu-west-1b 10.20.1.0/24       SG: 22 from your IP only
                                                    80 and 5000 from anywhere
                                                    all outbound
```

## Layout

```
terraform/
├── versions.tf               Terraform and provider versions
├── providers.tf              AWS provider + default tags
├── backend.tf                S3 remote state (partial config)
├── backend.hcl.example       template for backend.hcl
├── variables.tf              inputs, with validation
├── main.tf                   wires the three modules together
├── outputs.tf                IP, IDs, ssh command etc.
├── terraform.tfvars.example  template for terraform.tfvars
├── bootstrap/                one-off stack that creates the state bucket
└── modules/
    ├── network/              VPC, subnets (for_each), IGW, route table
    ├── security/             security group + rules (for_each)
    └── compute/              Ubuntu AMI lookup, key pair, EC2 instance, user data
```

## Prerequisites

- Terraform 1.10 or newer (`terraform version`). 1.10 is needed for S3 state locking.
- AWS CLI v2, logged in with an IAM user that can manage EC2, VPC and S3
  (`aws sts get-caller-identity` should print your account).
- An SSH key pair. The default path is `~/.ssh/sokosmart_f3`:
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/sokosmart_f3 -C sokosmart-f3
  ```
- Your public IP, for the SSH rule: `curl https://checkip.amazonaws.com`

No AWS keys go in this folder. The provider reads them from your AWS CLI
profile or the usual `AWS_*` environment variables.

## Usage

All commands run from the `terraform/` folder.

**1. Create the state bucket (once per AWS account)**

```bash
terraform -chdir=bootstrap init
terraform -chdir=bootstrap apply
terraform -chdir=bootstrap output -raw backend_hcl > backend.hcl
```

The bucket is versioned, encrypted and blocks all public access. Its own
state stays local in `bootstrap/terraform.tfstate` (gitignored).

**2. Set your variables**

```bash
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: at least ssh_allowed_cidrs = ["<your-ip>/32"]
```

**3. Init, check, plan, apply**

```bash
terraform init -backend-config=backend.hcl
terraform fmt -recursive -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

The plan creates 16 resources. Afterwards:

```bash
terraform output
ssh -i ~/.ssh/sokosmart_f3 ubuntu@$(terraform output -raw instance_public_ip)
```

**4. Destroy when done**

```bash
terraform destroy
```

The state bucket is left alone. To remove it too, run
`terraform -chdir=bootstrap destroy -var force_destroy=true`.

## Variables

| Name | Type | Default | Notes |
|---|---|---|---|
| `aws_region` | string | `eu-west-1` | must look like a region code |
| `aws_profile` | string | `null` | AWS CLI profile; null uses env vars or default |
| `project` | string | `sokosmart` | name prefix, lowercase, 3-21 chars |
| `environment` | string | `dev` | one of `dev`, `staging`, `prod` |
| `owner` | string | `group-7` | goes in the `Owner` tag |
| `extra_tags` | map(string) | `{}` | added to every resource |
| `vpc_cidr` | string | `10.20.0.0/16` | must be a valid CIDR |
| `public_subnet_count` | number | `2` | 1 to 3, one per AZ |
| `ssh_allowed_cidrs` | list(string) | **required** | your IP as /32; `0.0.0.0/0` is rejected |
| `app_allowed_cidrs` | list(string) | `["0.0.0.0/0"]` | who can reach ports 80 and the app port |
| `app_port` | number | `5000` | gunicorn port from the Dockerfile |
| `instance_type` | string | `t3.micro` | limited to `t2.micro`, `t3.micro`, `t3.small` |
| `ssh_public_key_path` | string | `~/.ssh/sokosmart_f3.pub` | public key loaded into the key pair |
| `root_volume_size` | number | `20` | GB, 8 to 30 (free tier max is 30) |

## Outputs

| Name | Description |
|---|---|
| `instance_public_ip` | public IP of the server (Ansible inventory) |
| `instance_public_dns` | public DNS name |
| `instance_id` | EC2 instance ID |
| `vpc_id` | VPC ID |
| `public_subnet_ids` | subnet IDs |
| `security_group_id` | app security group ID |
| `ami_id` | Ubuntu AMI that was used |
| `ssh_user` | `ubuntu` |
| `ssh_command` | ready-made ssh command |
| `app_url` | `http://<ip>:5000/health`, works once Ansible deploys the app |

## Design notes

- **Remote state:** S3 with native lockfile (`use_lockfile = true`), so no
  DynamoDB table is needed. Bucket and key come from `backend.hcl` because
  backend blocks can't use variables.
- **Validation:** region format, environment list, CIDR checks, allowed
  instance sizes, disk size range, and SSH can't be opened to the world.
- **for_each:** subnets are keyed by AZ and security group rules by
  `port-cidr`, so adding an IP adds one rule instead of reshuffling a list.
- **Tagging standard:** `Project`, `Environment`, `Owner`, `ManagedBy`,
  `Repository` on everything through provider `default_tags`, plus `Name`
  per resource. The instance also has `Role = app`.
- **Hardening:** IMDSv2 required, encrypted gp3 root disk, the VPC default
  security group is emptied, subnets don't hand out public IPs by default,
  every rule has a description.
- **User data** only sets the hostname and makes sure python3 is there.
  Everything else (Docker, the app, firewall, SSH hardening) is Ansible's job.

## For Ansible (Part 2)

- Host: `terraform output -raw instance_public_ip`, user `ubuntu`,
  key `~/.ssh/sokosmart_f3`.
- For the `aws_ec2` dynamic inventory, filter on
  `tag:Project = sokosmart` and `tag:Role = app`, region `eu-west-1`.
- Port 5000 is already open in the security group.

## Troubleshooting

**`Failed to load plugin schemas ... x509: certificate signed by unknown authority`**
(Windows): antivirus HTTPS scanning (we hit this with Avast) breaks the local
TLS link between Terraform and the provider. Either add the project folder
to the antivirus exceptions or set this before running Terraform:

```powershell
$env:TF_DISABLE_PLUGIN_TLS = "1"
```

This only affects the local link between the two processes. Calls to AWS are
still HTTPS.

**`Backend initialization required`**: you skipped step 1, or forgot
`-backend-config=backend.hcl` on `terraform init`.
