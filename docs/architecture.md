# Architecture (Formative 1)

SokoSmart starts as one service (`price-service`) with clear layers so it can be
split into microservices later:

```
HTTP request -> routes.py (API layer) -> services.py (business logic) -> repository.py (data access)
```

- **routes.py**: parses requests, returns JSON. No business logic.
- **services.py**: validation, filtering, summaries, comparisons.
- **repository.py**: the only place that touches storage (in-memory/JSON today, PostgreSQL later).

Planned services: `price-service` (now), `ussd-service`, `web-dashboard`, `notification-service`.

## Infrastructure and deployment

Terraform in terraform/ uses AWS to create the network, security groups and an
Ubuntu EC2 server. Ansible connects over SSH and applies four roles: docker,
ssh_hardening, firewall and app. The price service runs as the Dockerfile's
unprivileged user on port 5000 and exposes /health. Runtime environment settings
are supplied separately from the image. The image can be pulled from a registry
or loaded from a controller-built archive, matching the server architecture.

SSH accepts keys only from the deployment user. UFW restricts inbound traffic,
and a DOCKER-USER policy also filters published Docker ports. Terraform's
security groups provide a separate network layer. AWS provisioning and local
Docker verification are distinct; local test results do not prove EC2 deployment.

The current in-memory repository loses new reports when the app is replaced.
PostgreSQL persistence and automatic image publishing are separate tasks.
