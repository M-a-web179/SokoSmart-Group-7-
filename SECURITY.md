# Security Policy

## Reporting a vulnerability

Report suspected vulnerabilities privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue for security problems. We aim to acknowledge reports within 3 working days.

## Automated scans

| Scan | Tool | What it checks | Threshold | Workflow |
|---|---|---|---|---|
| Python dependencies | pip-audit | `requirements.txt` and `requirements-dev.txt` against known advisories | Any known vulnerability fails the job | `security.yml` |
| Container image | Trivy 0.57.1 | OS packages and Python packages in the built image | HIGH and CRITICAL with an available fix fail the job | `security.yml` |
| Infrastructure as Code | Checkov | Terraform in `terraform/` | Any failed check not in the documented skip list fails the job | `security.yml` |
| Secrets | Gitleaks | Commits and pull requests for committed secrets | Any detected secret fails the job | `secret-scanning.yml` |
| Dependency updates | Dependabot | Outdated dependencies | Automatic update pull requests | `dependabot.yml` |

The `security.yml` scans run on every pull request into `main` and on every push to `main`.

## Findings and fixes

### Container image (Trivy)

The first scan of the image reported 53 HIGH or CRITICAL findings, all with fixes available.

| Area | Findings | Cause | Fix |
|---|---|---|---|
| Debian OS packages | 50 (43 HIGH, 7 CRITICAL) in apt, gnutls, krb5, libcap2, pam, pcre2, openssl, perl and others | The pinned base image `python:3.11.13-slim-bookworm` was behind Debian security updates | `apt-get upgrade` in the runtime stage of the `Dockerfile` |
| Python packaging tools | 3 HIGH: setuptools (CVE-2024-6345, CVE-2025-47273) and wheel (CVE-2026-24049) | Old versions shipped inside the base image, not in the application requirements | Upgrade to setuptools 78.1.1 or later and wheel 0.46.2 or later in the `Dockerfile` |

After the fix, the Trivy job passes.

### Python dependencies (pip-audit)

No known vulnerabilities in the application or development requirements.

### Infrastructure as Code (Checkov)

The first scan of the network and compute code had 38 passed and 10 failed checks. None is a critical misconfiguration. SSH is not open to the world, the instances require IMDSv2, the root volumes are encrypted, and the Terraform state bucket is private, versioned, encrypted and blocks public access.

Adding the database, registry, secret and IAM code produced 11 further failed checks. One was fixed in code: RDS PostgreSQL and upgrade logs are now exported to CloudWatch (CKV_AWS_129). One is a false positive handled by an inline skip on a single resource (CKV_AWS_24). The other 9 are accepted risks listed below. All are skipped by ID in `security.yml`, except the inline one.

The app VM has an instance profile that can only pull from the `sokosmart-price` ECR repository and read the one database secret. ECR authentication uses `ecr:GetAuthorizationToken`, which AWS only allows on all resources.

## Accepted risks

| Check | Resource | Justification |
|---|---|---|
| CKV_AWS_88 | Bastion host | Only the bastion has a public IP, because it is the single SSH entry point into the VPC. The app VM sits in a private subnet with no public IP and reaches the internet through the NAT gateway. SSH to the bastion is limited to admin IPs by security group rules. |
| CKV_AWS_126 | EC2 instances | Detailed monitoring is a paid feature and is not needed for a short-lived student environment. |
| CKV2_AWS_41 | Bastion host | The app VM has an instance profile with least-privilege access. The bastion only forwards SSH and HTTP and makes no AWS API calls, so a role would grant nothing it needs. |
| CKV2_AWS_5 | Security groups | The groups are attached to instances through the compute and database modules. Checkov does not follow the reference across module boundaries, so this is a false positive. |
| CKV2_AWS_11 | VPC | VPC flow logs add cost and the environment is short-lived. |
| CKV_AWS_394 | Availability zones data source | Low impact. Zone selection is controlled by the AWS region variable. |
| CKV_AWS_18 | Terraform state bucket | Access logging is not needed for a small private state bucket. |
| CKV2_AWS_62 | Terraform state bucket | Event notifications are not used. |
| CKV_AWS_144 | Terraform state bucket | Cross-region replication is not needed. The bucket is versioned. |
| CKV_AWS_145 | Terraform state bucket | The bucket uses SSE-S3 encryption. A customer-managed KMS key adds cost and complexity without a requirement for it. |
| CKV_AWS_353 | RDS instance | Performance Insights adds no value on the smallest instance class for a short demo. The PostgreSQL logs are exported to CloudWatch instead. |
| CKV_AWS_118 | RDS instance | Enhanced monitoring needs an extra IAM role and adds cost. Standard CloudWatch metrics and log exports cover the demo. |
| CKV_AWS_293 | RDS instance | Deletion protection would block `terraform destroy`, which is required to stop hourly costs after the demo. The database holds no production data. |
| CKV_AWS_157 | RDS instance | Multi-AZ doubles the hourly cost. The database is a single-instance demo environment with a one-day backup retention. |
| CKV2_AWS_30 | RDS instance | Query logging needs a custom parameter group. PostgreSQL logs are exported to CloudWatch, which meets the demo's logging need. |
| CKV_AWS_149 | Secrets Manager secret | The secret is encrypted with the AWS-managed key. A customer-managed KMS key adds cost without a requirement for it. |
| CKV_AWS_136 | ECR repository | The repository is encrypted with AES256. A customer-managed KMS key adds cost without a requirement for it. |
| CKV2_AWS_57 | Secrets Manager secret | No rotation function is deployed. The password is generated once by Terraform and the environment is destroyed after the demo. |
| CKV_AWS_24 | App SSH ingress rule | Inline skip on this one rule. The source is the bastion security group, not a CIDR range, so SSH is not open to the world. Checkov does not evaluate the security group reference. |

Trivy runs with `--ignore-unfixed`. Vulnerabilities with no vendor fix yet are not reported, because the build cannot remediate them. They are picked up automatically once a fix is published, since every pull request rebuilds the image and rescans it.

## Ongoing practice

- The base image is pinned, so new CVEs can appear over time. A failing Trivy job on a pull request means the Dockerfile layer or base image needs updating.
- New accepted risks must be added to this file with a justification at the same time as they are added to the Checkov skip list.
- Secrets are never committed. Configuration comes from environment variables and Terraform variables, and Gitleaks checks every pull request.

Last reviewed: 20 November 2026.