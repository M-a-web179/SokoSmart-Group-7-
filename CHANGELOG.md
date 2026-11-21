# Changelog

All notable changes to SokoSmart are recorded here, grouped by assignment milestone.

## Summative: The Complete DevOps Pipeline (2026-11-14 to 2026-11-21)

### Added
- Private network with NAT gateway, bastion host and private app VM (#65).
- ECR repository with immutable tags, RDS PostgreSQL 16, the security group chain and an IAM instance profile for the app VM (#68).
- `/health` and `/ready` endpoints and structured JSON logging (#66).
- Terraform cloud provider configuration and AWS verification evidence (#58, #59).
- Live deployment on AWS eu-west-1 behind an nginx reverse proxy on the bastion.

### Changed
- Terraform moved from local verification to a real AWS apply with remote state in S3.

### Known limitations
- The price repository is in memory, so reports POSTed to the API are lost when the container restarts.

## F3: Infrastructure and Security (2026-11-09 to 2026-11-10)

### Added
- F3 group setup plan and milestone issues (#32).
- Terraform modules for the SokoSmart app server on AWS (#51).
- DevSecOps scans in CI: pip-audit, Trivy and Checkov, with SECURITY.md (#53).
- Ansible deployment with docker, ssh_hardening, firewall and app roles (#55).
- Web dashboard and CONTRIBUTING guide (#8).

## F2: Containers and CI (2026-10-31)

### Added
- USSD menu, multi-stage Dockerfile with a non-root user, Docker Compose with gunicorn, Dependabot and secret scanning (#7).
- Docker setup and instructions (#15).

## F1: Foundation (2026-10-22 to 2026-10-23)

### Added
- Price service core with API, service and repository layers (#2).
- Enforced Python lint and formatting checks in CI (#5).