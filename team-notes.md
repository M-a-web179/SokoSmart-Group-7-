# Contribution notes

## domyusuf — Ansible deployment

I added four roles to configure our Ubuntu server: Docker installation, app
deployment, firewall rules and SSH hardening. The playbook runs the actual
SokoSmart price service on port 5000 and checks /health. It can pull a published
image or transfer a docker save archive over SSH. This lets us test our current
Dockerfile without depending on a registry upload.

I tested this on a fresh local Ubuntu 22.04 systemd container over SSH using my
own key. The server's host key was recorded locally, and host key checking stayed
on. The private key and local settings are outside the committed files.

- Ansible ping returned pong.
- First run: ok=27, changed=17, unreachable=0, failed=0.
- Second run: ok=23, changed=0, unreachable=0, failed=0.
- /health returned HTTP 200 and identified the price-service.
- /api/prices returned 12 seeded records.
- sshd -t passed. Root, password and keyboard-interactive login are disabled.
- UFW permits SSH from the test gateway /32 and app traffic on 5000.
- A separate test client reached 5000 but could not reach a test Docker port
  9000, even though the probe server itself returned HTTP 200 internally.
- Ansible lint passed with zero failures and zero warnings in its rule summary.
- I removed the app container and image, the outer Ubuntu test container and
  fixture image, and the controller's app test image. Docker inspection confirms
  they no longer exist. After cleanup, port 5000 returned HTTP 403 from macOS
  AirTunes rather than SokoSmart; the cleanup log includes the response headers.

The second run made no changes because package, service, file and container
modules compare the current state with what we declared. Templates notify
restart handlers only when they change. The image archive is loaded only if it
changes or the image is missing. Health requests only read state. New image tags
or configuration changes should still cause real changes on the next run.

The first image build timed out fetching the Python base image. Pulling the base
image separately and retrying the unchanged Dockerfile worked. This did not
require changing the app or its dependencies.

Evidence is in evidence/domyusuf, with the source commit and image ID recorded
in image-source.json. The logs are from this SokoSmart deployment. The screenshot shows the prices API because main does not have a dashboard
route yet.

### What this proves and what remains

Terraform in this repo uses AWS. These results are from the local Docker test
track; I did not run an AWS apply or destroy and am not claiming EC2 deployment
evidence. Once the AWS server is available, the same playbook can use its IP and
Ubuntu user from Terraform outputs. The inventory helper reads those outputs
without changing infrastructure.

Our price repository currently stores reports in memory. Replacing the container
loses newly added reports; PostgreSQL persistence remains separate work. Image
publishing, dynamic cloud inventory, fail2ban and unattended upgrades are also
outside this change. M-a-web179's DevSecOps workflow is being handled separately.

Task: https://github.com/M-a-web179/SokoSmart-Group-7-/issues/54

PR: https://github.com/M-a-web179/SokoSmart-Group-7-/pull/55

The issue and PR screenshots are saved alongside the runtime evidence.
