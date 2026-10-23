# Terraform Plan — SokoSmart on AWS

> Status: **plan only** (Formative 1). Nothing is applied yet; this directory
> holds the reviewed `terraform plan` for the first deployment.

## Target architecture

```
Internet
   │  :80
   ▼
Application Load Balancer ── health check /health
   │
   ▼
ECS Fargate service "price-service" (2 tasks, 0.25 vCPU / 512 MB)
   │  image from ECR: sokosmart/price-service (scan-on-push enabled)
   ▼
CloudWatch Logs (/ecs/sokosmart-dev-price-service, 14-day retention)
```

All resources live in a dedicated VPC (`10.20.0.0/16`, two public subnets
across two AZs). The app security group only accepts traffic on port 5000
from the ALB security group — nothing is exposed directly.

## Files

| File | Purpose |
|---|---|
| `versions.tf` | Terraform ≥ 1.5, AWS provider ~> 5.0, commented S3 backend for remote state |
| `variables.tf` | Region, project, environment, image, port, task count, VPC CIDR |
| `main.tf` | Provider, VPC/networking, ALB, ECR, ECS cluster + task definition + service, IAM, logs |
| `outputs.tf` | ALB DNS name, ECR repository URL, cluster name, health-check URL |

## Verified plan (terraform v1.17.0, AWS provider ~> 5.0)

```
Plan: 19 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + alb_dns_name       = (known after apply)
  + ecr_repository_url = (known after apply)
  + ecs_cluster_name   = "sokosmart-dev"
  + health_check_url   = (known after apply)
```

The 19 resources:

| Group | Resources |
|---|---|
| Network (7) | `aws_vpc`, 2× `aws_subnet`, `aws_internet_gateway`, `aws_route_table`, 2× `aws_route_table_association`* |
| Security (2) | `aws_security_group.alb` (HTTP 80 from internet), `aws_security_group.app` (port 5000 from ALB only) |
| Load balancing (3) | `aws_lb`, `aws_lb_target_group` (health check `/health`), `aws_lb_listener` |
| Containers (4) | `aws_ecr_repository` (immutable tags, scan on push), `aws_cloudwatch_log_group`, `aws_ecs_cluster`, `aws_ecs_task_definition` |
| Service (1) | `aws_ecs_service` (Fargate, 2 tasks) |
| IAM (2) | `aws_iam_role.ecs_execution`, `aws_iam_role_policy_attachment` (AWS managed execution policy) |

\* counted with the network group above.

## How to reproduce the plan

```bash
cd infra
terraform init
terraform validate
terraform plan          # plan_only=true by default: no AWS credentials needed
```

## Applying for real (next formative)

1. Provide credentials: `export AWS_PROFILE=sokosmart` (least-privilege IAM user or SSO role).
2. Disable plan-only mode: `export TF_VAR_plan_only=false`.
3. Copy `terraform.tfvars.example` → `terraform.tfvars` and set the real image after CI pushes to ECR.
4. Enable the S3 backend in `versions.tf` (state + DynamoDB locking) before the first apply.
5. `terraform plan -out=tfplan && terraform apply tfplan`.
