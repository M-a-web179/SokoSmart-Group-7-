output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC."
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets, in AZ order."
  value       = [for az in sort(keys(aws_subnet.public)) : aws_subnet.public[az].id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets, in AZ order. Two AZs, so RDS can use them."
  value       = [for az in sort(keys(aws_subnet.private)) : aws_subnet.private[az].id]
}

output "private_subnet_cidrs" {
  description = "CIDR blocks of the private subnets."
  value       = [for az in sort(keys(aws_subnet.private)) : aws_subnet.private[az].cidr_block]
}

output "nat_gateway_id" {
  description = "ID of the NAT gateway."
  value       = aws_nat_gateway.this.id
}

output "nat_public_ip" {
  description = "Public IP the private subnets use for outbound traffic."
  value       = aws_eip.nat.public_ip
}

output "internet_gateway_id" {
  description = "ID of the internet gateway."
  value       = aws_internet_gateway.this.id
}
