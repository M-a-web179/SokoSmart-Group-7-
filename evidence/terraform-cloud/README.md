# Evidence: Terraform on AWS (12 November 2026)

- ansible-run1.txt, ansible-run2.txt: Ansible runs (changed=13, then changed=0)
- aws-verification.txt: terraform outputs after apply, external /health and /api/prices responses, UFW, container and SSH status, copied from the terminal session with the admin IP redacted
- terraform-destroy-and-checks.png: screenshot of the destroy result (16 destroyed) and the post-destroy checks (instance terminated, no VPC, no key pair, empty Terraform state)

Not saved: the console output of terraform apply, and screenshots of the AWS console.