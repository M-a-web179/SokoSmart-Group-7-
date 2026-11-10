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

The first scan had 38 passed and 10 failed checks. None is a critical misconfiguration. SSH is not open to the world, the instance requires IMDSv2, the root volume is encrypted, and the Terraform state bucket is private, versioned, encrypted and blocks public access. The 10 failed checks are documented as accepted risks below and are skipped by ID in `security.yml`.

## Accepted risks

| Check | Resource | Justification |
|---|---|---|
| CKV_AWS_88 | EC2 instance | The instance has a public IP so users and Ansible can reach it directly. A bastion host or NAT gateway is out of scope and adds cost. Ingress is limited by security group rules. |
| CKV_AWS_126 | EC2 instance | Detailed monitoring is a paid feature and is not needed for a single `t3.micro` student environment. |
| CKV2_AWS_41 | EC2 instance | The application makes no AWS API calls, so an instance role would grant no needed permissions. |
| CKV2_AWS_5 | Security group | The security group is attached to the instance through the compute module. Checkov does not follow the reference across module boundaries, so this is a false positive. |
| CKV2_AWS_11 | VPC | VPC flow logs add cost and the environment is short-lived. |
| CKV_AWS_394 | Availability zones data source | Low impact. Zone selection is controlled by the AWS region variable. |
| CKV_AWS_18 | Terraform state bucket | Access logging is not needed for a small private state bucket. |
| CKV2_AWS_62 | Terraform state bucket | Event notifications are not used. |
| CKV_AWS_144 | Terraform state bucket | Cross-region replication is not needed. The bucket is versioned. |
| CKV_AWS_145 | Terraform state bucket | The bucket uses SSE-S3 encryption. A customer-managed KMS key adds cost and complexity without a requirement for it. |

Trivy runs with `--ignore-unfixed`. Vulnerabilities with no vendor fix yet are not reported, because the build cannot remediate them. They are picked up automatically once a fix is published, since every pull request rebuilds the image and rescans it.

## Ongoing practice

- The base image is pinned, so new CVEs can appear over time. A failing Trivy job on a pull request means the Dockerfile layer or base image needs updating.
- New accepted risks must be added to this file with a justification at the same time as they are added to the Checkov skip list.
- Secrets are never committed. Configuration comes from environment variables and Terraform variables, and Gitleaks checks every pull request.

Last reviewed: 10 November 2026.