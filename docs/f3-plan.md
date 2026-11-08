# Formative 3 plan: group setup (Part A)

Decisions for F3 (Terraform, Ansible, DevSecOps). Tracked in milestone
**Formative 3 - Infrastructure & Security** (issues #27 to #31).

## Deadline
| Item | Value |
|---|---|
| Team target | Sunday 2026-11-08, 23:59 CAT (UTC+2) |
| Official Canvas deadline | Check Canvas; must not be earlier than the team target |
| Demo date | None announced |

The milestone due date matches the team target.

## Split of work
| Part | Points | Scope |
|---|---|---|
| A. Group setup | n/a | This document, issues #27 to #31 (HelloWorldVictor) |
| B. Part 1: Terraform | 40 | `terraform/` with network, security and compute modules |
| C. Part 2: Ansible | 30 | `ansible/` with docker, app, firewall and ssh_hardening roles |
| D. Part 3: DevSecOps | 30 | `security.yml` (pip-audit, Trivy, Checkov), `SECURITY.md` |

Each part owner opens one issue per task under the F3 milestone, assigns
themselves, and works on one branch and PR per task.

## Cloud provider
| Item | Value |
|---|---|
| Provider | AWS |
| Why | README already plans Terraform on AWS, PR #8 used AWS, and the Ansible mastery extra uses the `aws_ec2` dynamic inventory |
| Region | `eu-west-1` (set in a variable, not hardcoded) |
| Instance | `t3.micro` (free tier eligible) |
| App port | 5000 (gunicorn, from the root `Dockerfile`) |
| Credentials | Each person uses their own AWS profile or env vars. Never commit keys, `.tfvars` or `.tfstate`. |

## PR order
1. **Terraform** (Part 1) merges first. It creates the server that the other parts use.
2. **Ansible** (Part 2) and **Checkov** (Part 3) start after it, because Ansible needs the
   instance's public IP (Terraform output) and Checkov scans `terraform/`.
3. pip-audit and Trivy (Part 3) do not depend on Terraform and can merge at any time.

Every PR needs 1 approval and green `lint`, `test` and `docker` checks (the "Project main" ruleset).

## PR #8 decision: split
PR #8 bundles three things: the web dashboard, CONTRIBUTING.md, and an `infra/` Terraform
plan for ECS Fargate behind a load balancer.

F3 needs a single EC2 instance that Ansible can SSH into, laid out as `terraform/` modules.
ECS Fargate has no server to configure, so that design does not fit.

Decision:
- PR #8 keeps the dashboard and CONTRIBUTING.md only. `infra/` is removed from it.
- The ECS, ALB, ECR, CloudWatch and IAM resources are dropped.
- The network code is reusable for the Terraform owner. It is in commit `d49206c`
  (`git show d49206c:infra/main.tf`):

| PR #8 resource | Reuse in |
|---|---|
| `aws_vpc.main`, `aws_subnet.public` (count = 2), `aws_internet_gateway.main`, `aws_route_table.public`, `aws_route_table_association.public` | `terraform/modules/network` |
| `aws_security_group.app` and the egress rule | `terraform/modules/security` (add SSH from a restricted CIDR, app port 5000) |
| `default_tags` in the provider block | tagging standard (mastery extra) |
| Commented S3 + DynamoDB backend in `infra/versions.tf` | remote state (mastery extra) |
