locals {
  # Build one entry per (port, cidr) pair so every rule is its own resource.
  # Keys look like "ssh-203.0.113.10/32" which keeps plans readable.
  ingress_rules = merge(
    {
      for cidr in var.ssh_allowed_cidrs : "ssh-${cidr}" => {
        port        = 22
        cidr        = cidr
        description = "SSH from allowed admin IP"
      }
    },
    {
      for cidr in var.app_allowed_cidrs : "http-${cidr}" => {
        port        = 80
        cidr        = cidr
        description = "HTTP"
      }
    },
    {
      for cidr in var.app_allowed_cidrs : "app-${cidr}" => {
        port        = var.app_port
        cidr        = cidr
        description = "price-service app port"
      }
    },
  )
}

resource "aws_security_group" "app" {
  name        = "${var.name}-app-sg"
  description = "SokoSmart app server: SSH from admin IPs, HTTP and app port"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name}-app-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "this" {
  for_each = local.ingress_rules

  security_group_id = aws_security_group.app.id
  description       = each.value.description
  ip_protocol       = "tcp"
  from_port         = each.value.port
  to_port           = each.value.port
  cidr_ipv4         = each.value.cidr

  tags = {
    Name = "${var.name}-${each.key}"
  }
}

# Server needs to reach apt mirrors, Docker Hub, GHCR etc.
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.app.id
  description       = "Allow all outbound traffic"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"

  tags = {
    Name = "${var.name}-egress-all"
  }
}
