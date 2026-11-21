# SokoSmart infrastructure (Terraform)

Terraform for the Summative project. It builds a private, production-style stack on AWS in eu-west-1: a VPC with public and private subnets, a bastion host, a private app VM, a PostgreSQL RDS instance, a private ECR repository and the security groups and IAM that connect them. Ansible then deploys the price-service onto the app VM.

```
Internet
   │
   ▼
Internet gateway
   │
VPC 10.20.0.0/16
 ├─ public subnets (2 AZs)  ── bastion host (SSH from admin IP, HTTP 80 from the internet)
 │                             NAT gateway (outbound only)
 └─ private subnets (2 AZs) ── app VM (no public IP, reached through the bastion)
                               RDS PostgreSQL (reachable only from the app security group)

ECR (private, immutable tags)    Secrets Manager (database credentials)
```

## Layout

```
terraform/
├── versions.tf               Terraform and provider versions
├── providers.tf              AWS provider and default tags
├── backend.tf                S3 remote state (partial config)
├── backend.hcl.example       template for backend.hcl
├── variables.tf              inputs, with validation
├── main.tf                   wires the modules together
├── outputs.tf                IPs, IDs, endpoints, secret ARN
├── terraform.tfvars.example  template for terraform.tfvars
├── bootstrap/                one-off stack that creates the state bucket
└── modules/
    ├── network/              VPC, public and private subnets, internet gateway, NAT gateway, routes
    ├── security/             security groups and rules
    ├── ecr/                  private ECR repository
    ├── database/             RDS PostgreSQL and the Secrets Manager secret
    ├── iam/                  instance profile for the app VM
    └── compute/              Ubuntu AMI lookup, key pair, bastion and app VM
```

## Prerequisites

- Terraform 1.10 or newer (`terraform version`). 1.10 is needed for S3 state locking.
- AWS CLI v2 with an IAM user that can manage EC2, VPC, RDS, ECR, IAM, Secrets Manager and S3 (`aws sts get-caller-identity` should print your account).
- An SSH key pair. The default path is `~/.ssh/sokosmart_f3`:
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/sokosmart_f3 -C sokosmart-f3
  ```
- Your public IP for the SSH rule: `curl https://checkip.amazonaws.com`

No AWS keys go in this folder. The provider reads them from your AWS CLI profile or the usual `AWS_*` environment variables.

## Usage

All commands run from the `terraform/` folder.

**1. Create the state bucket (once per AWS account)**

```bash
terraform -chdir=bootstrap init
terraform -chdir=bootstrap apply
terraform -chdir=bootstrap output -raw backend_hcl > backend.hcl
```

The bucket is versioned, encrypted and blocks all public access. Its own state stays local in `bootstrap/terraform.tfstate` (gitignored).

**2. Set your variables**

```bash
cp terraform.tfvars.example terraform.tfvars
```

Set `ssh_allowed_cidrs` to your public IP as a `/32`.

**3. Init, check, plan, apply**

```bash
terraform init -backend-config=backend.hcl
terraform fmt -recursive -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

The apply creates 45 resources. Afterwards:

```bash
terraform output
terraform output -json > outputs.json
```

`outputs.json` feeds `ansible/inventory_from_terraform.py`. Connect to the private app VM through the bastion with the `ssh_command` output.

**4. Destroy when done**

```bash
terraform destroy
```

The state bucket is left alone. To remove it too, run `terraform -chdir=bootstrap destroy -var force_destroy=true`. The NAT gateway and RDS instance cost money while they exist, so destroy the stack as soon as it is no longer needed.

## Variables

| Name | Type | Default | Notes |
|---|---|---|---|
| `aws_region` | string | `eu-west-1` | must look like a region code |
| `aws_profile` | string | `null` | AWS CLI profile; null uses env vars or the default profile |
| `project` | string | `sokosmart` | name prefix, lowercase, 3-21 chars |
| `environment` | string | `dev` | one of `dev`, `staging`, `prod` |
| `owner` | string | `group-7` | goes in the `Owner` tag |
| `extra_tags` | map(string) | `{}` | added to every resource |
| `vpc_cidr` | string | `10.20.0.0/16` | must be a valid CIDR |
| `public_subnet_count` | number | `2` | 2 or 3 availability zones; one public and one private subnet in each |
| `ssh_allowed_cidrs` | list(string) | **required** | your IP as /32; `0.0.0.0/0` is rejected |
| `app_port` | number | `5000` | gunicorn port from the Dockerfile |
| `app_allowed_cidrs` | list(string) | `["0.0.0.0/0"]` | who can reach the app and HTTP ports |
| `instance_type` | string | `t3.micro` | limited to `t2.micro`, `t3.micro`, `t3.small` |
| `ssh_public_key_path` | string | `~/.ssh/sokosmart_f3.pub` | public key loaded into the key pair |
| `root_volume_size` | number | `20` | GB, 8 to 30 |

## Outputs

| Name | Description |
|---|---|
| `bastion_public_ip` | public IP of the bastion, the only SSH entry point |
| `bastion_instance_id` | bastion instance ID |
| `app_private_ip` | private IP of the app VM |
| `app_instance_id` | app VM instance ID |
| `vpc_id` | VPC ID |
| `public_subnet_ids` | public subnet IDs |
| `private_subnet_ids` | private subnet IDs, used by the app VM and the RDS subnet group |
| `nat_public_ip` | outbound IP of the private subnets |
| `ami_id` | Ubuntu AMI used for the instances |
| `ssh_user` | `ubuntu` |
| `ssh_command` | ready-made SSH command to the app VM through the bastion |
| `ecr_repository_url` | private registry URL for docker push and pull |
| `db_endpoint` | RDS host name |
| `db_port` | RDS port |
| `db_name` | database name |
| `db_secret_arn` | ARN of the Secrets Manager secret with the database credentials |

## Design notes

- **Remote state:** S3 with native lockfile (`use_lockfile = true`), so no DynamoDB table is needed. Bucket and key come from `backend.hcl` because backend blocks can't use variables.
- **Network isolation:** the app VM has no public IP and reaches the internet only through the NAT gateway. RDS sits in the private subnets and accepts connections only from the app security group.
- **Validation:** region format, environment list, CIDR checks, allowed instance sizes, disk size range, and SSH can't be opened to the world.
- **Tagging standard:** `Project`, `Environment`, `Owner`, `ManagedBy`, `Repository` on everything through provider `default_tags`, plus `Name` per resource.
- **Registry:** ECR tags are immutable, so every image is tagged with its commit SHA and `latest` is never used.
- **Secrets:** the database credentials live in Secrets Manager. The app VM reads them through its instance profile, so no password is stored in the repository.
- **Checkov:** CI scans this folder on every pull request. A deliberate failure is recorded in `evidence/summative/checkov-failure.txt`.

## For Ansible

- Export the outputs with `terraform output -json > outputs.json`.
- Generate the inventory and settings with `python3 ansible/inventory_from_terraform.py --key ~/.ssh/sokosmart_f3 --image-tag <short SHA> --outputs outputs.json`.
- Ansible reaches the app VM through the bastion. See `ansible/README.md` for the full flow.

## Evidence

Apply output, plan output and the architecture diagram are in `evidence/summative/`.

## Troubleshooting

**`Failed to load plugin schemas ... x509: certificate signed by unknown authority`** (Windows): antivirus HTTPS scanning breaks the local TLS link between Terraform and the provider. Add the project folder to the antivirus exceptions or set this before running Terraform:

```powershell
$env:TF_DISABLE_PLUGIN_TLS = "1"
```

This only affects the local link between the two processes. Calls to AWS are still HTTPS.

**`Backend initialization required`**: you skipped step 1, or forgot `-backend-config=backend.hcl` on `terraform init`.

**SSH to the bastion times out:** your public IP has probably changed. Update `ssh_allowed_cidrs` in `terraform.tfvars`, then plan and apply.