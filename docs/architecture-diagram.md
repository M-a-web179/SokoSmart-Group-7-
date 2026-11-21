# Architecture diagram

```mermaid
flowchart LR
    users["Users<br/>browser or curl"]
    admin["Admin laptop<br/>SSH from allowed IP"]
    gha["GitHub Actions<br/>CD on push to main"]

    subgraph aws["AWS eu-west-1"]
        ecr["ECR sokosmart-price<br/>immutable commit SHA tags"]
        sm["Secrets Manager<br/>database secret"]

        subgraph vpc["VPC"]
            subgraph pub["Public subnet"]
                bastion["Bastion 3.255.170.205<br/>nginx reverse proxy on 80<br/>SSH on 22"]
                nat["NAT gateway<br/>EIP 52.209.153.9"]
            end

            subgraph priv["Private subnets in two AZs"]
                app["App VM 10.20.10.65<br/>Docker Compose, gunicorn on 5000<br/>no public IP"]
                rds[("RDS PostgreSQL 16<br/>db sokosmart<br/>not publicly accessible")]
            end
        end
    end

    users -->|"HTTP 80"| bastion
    admin -->|"SSH 22"| bastion
    gha -->|"SSH 22 for Ansible<br/>temporary SG rule"| bastion
    gha -->|"docker push"| ecr
    bastion -->|"proxy to 5000"| app
    bastion -->|"SSH 22 jump"| app
    app -->|"5432 with SSL"| rds
    app -->|"443 outbound"| nat
    nat -->|"image pull"| ecr
    nat -->|"secret read"| sm
```

## Network rules

| Layer | Rule |
|---|---|
| Bastion SG | HTTP 80 from the internet, SSH 22 from the admin IP and from the CD runner for the duration of a deploy |
| App SG | SSH 22 and TCP 5000 from the bastion SG only; outbound 80 and 443 to the internet and 5432 to the DB SG |
| DB SG | TCP 5432 from the app SG only, no CIDR rules |
| Egress path | Private subnets route through the NAT gateway to the public AWS endpoints (no VPC endpoints, to save cost) |