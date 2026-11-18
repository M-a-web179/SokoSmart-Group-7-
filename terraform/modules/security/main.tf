locals {
  bastion_ingress = merge(
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
        description = "Public HTTP, proxied to the app VM"
      }
    },
  )

  internet_egress_ports = {
    http  = 80
    https = 443
  }

  bastion_to_app_ports = {
    ssh = 22
    app = var.app_port
  }
}

resource "aws_security_group" "bastion" {
  name        = "${var.name}-bastion-sg"
  description = "Bastion host: SSH from admin IPs, public HTTP"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name}-bastion-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "app" {
  name        = "${var.name}-app-sg"
  description = "App VM: SSH and app port from the bastion only"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name}-app-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "db" {
  name        = "${var.name}-db-sg"
  description = "Database: PostgreSQL from the app VM only"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.name}-db-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "bastion" {
  for_each = local.bastion_ingress

  security_group_id = aws_security_group.bastion.id
  description       = each.value.description
  ip_protocol       = "tcp"
  from_port         = each.value.port
  to_port           = each.value.port
  cidr_ipv4         = each.value.cidr

  tags = {
    Name = "${var.name}-bastion-${each.key}"
  }
}

resource "aws_vpc_security_group_egress_rule" "bastion_to_app" {
  for_each = local.bastion_to_app_ports

  security_group_id            = aws_security_group.bastion.id
  description                  = "Bastion to app VM port ${each.value}"
  ip_protocol                  = "tcp"
  from_port                    = each.value
  to_port                      = each.value
  referenced_security_group_id = aws_security_group.app.id

  tags = {
    Name = "${var.name}-bastion-to-app-${each.key}"
  }
}

resource "aws_vpc_security_group_egress_rule" "bastion_internet" {
  for_each = local.internet_egress_ports

  security_group_id = aws_security_group.bastion.id
  description       = "Bastion outbound ${upper(each.key)} for updates"
  ip_protocol       = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_ipv4         = "0.0.0.0/0"

  tags = {
    Name = "${var.name}-bastion-out-${each.key}"
  }
}

resource "aws_vpc_security_group_ingress_rule" "app_from_bastion" {
  for_each = local.bastion_to_app_ports

  security_group_id            = aws_security_group.app.id
  description                  = "Port ${each.value} from the bastion"
  ip_protocol                  = "tcp"
  from_port                    = each.value
  to_port                      = each.value
  referenced_security_group_id = aws_security_group.bastion.id

  tags = {
    Name = "${var.name}-app-from-bastion-${each.key}"
  }
}

resource "aws_vpc_security_group_egress_rule" "app_to_db" {
  security_group_id            = aws_security_group.app.id
  description                  = "PostgreSQL to the database"
  ip_protocol                  = "tcp"
  from_port                    = var.db_port
  to_port                      = var.db_port
  referenced_security_group_id = aws_security_group.db.id

  tags = {
    Name = "${var.name}-app-to-db"
  }
}

resource "aws_vpc_security_group_egress_rule" "app_internet" {
  for_each = local.internet_egress_ports

  security_group_id = aws_security_group.app.id
  description       = "App outbound ${upper(each.key)} via NAT for ECR and packages"
  ip_protocol       = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_ipv4         = "0.0.0.0/0"

  tags = {
    Name = "${var.name}-app-out-${each.key}"
  }
}

resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  description                  = "PostgreSQL from the app VM"
  ip_protocol                  = "tcp"
  from_port                    = var.db_port
  to_port                      = var.db_port
  referenced_security_group_id = aws_security_group.app.id

  tags = {
    Name = "${var.name}-db-from-app"
  }
}