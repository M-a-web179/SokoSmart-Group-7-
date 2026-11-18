data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  # One public subnet per AZ, e.g. { "eu-west-1a" = "10.20.0.0/24", ... }
  azs = slice(data.aws_availability_zones.available.names, 0, var.public_subnet_count)
  public_subnets = {
    for i, az in local.azs : az => cidrsubnet(var.vpc_cidr, 8, i)
  }

  # Private subnets live in the same AZs, offset by 10 so the ranges
  # never overlap, e.g. 10.20.10.0/24 and 10.20.11.0/24. RDS needs at
  # least two AZs for its subnet group.
  private_subnets = {
    for i, az in local.azs : az => cidrsubnet(var.vpc_cidr, 8, i + 10)
  }

  # The NAT gateway sits in the first public subnet
  nat_az = local.azs[0]
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.name}-vpc"
  }
}

# Lock down the default SG that AWS creates with every VPC, so nothing
# can accidentally end up in it with open rules.
resource "aws_default_security_group" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.name}-default-sg"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.name}-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = each.key

  # Public IPs are given per instance instead (see compute module)
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.name}-public-${each.key}"
    Tier = "public"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.name}-public-rt"
  }
}

resource "aws_route" "internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

# ---------------------------------------------------------------- private tier

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.name}-private-${each.key}"
    Tier = "private"
  }
}

# Static public IP for the NAT gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name = "${var.name}-nat-eip"
  }

  depends_on = [aws_internet_gateway.this]
}

# One NAT gateway, not one per AZ. Lets the private app VM reach apt,
# Docker and ECR without having a public IP. A single NAT keeps the
# cost down; the trade-off is that losing its AZ cuts outbound access.
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[local.nat_az].id

  tags = {
    Name = "${var.name}-nat"
  }

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.name}-private-rt"
  }
}

# Outbound only: private subnets go out through the NAT, nothing comes in
resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this.id
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}
