output "bastion_public_ip" {
  description = "Public IP of the bastion host. The only SSH entry point."
  value       = module.compute.bastion_public_ip
}

output "bastion_instance_id" {
  description = "EC2 instance ID of the bastion host."
  value       = module.compute.bastion_instance_id
}

output "app_private_ip" {
  description = "Private IP of the app VM. Use it in the Ansible inventory with ProxyJump through the bastion."
  value       = module.compute.app_private_ip
}

output "app_instance_id" {
  description = "EC2 instance ID of the app VM."
  value       = module.compute.app_instance_id
}

output "vpc_id" {
  description = "ID of the VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets (two AZs). Used for the app VM and the RDS subnet group."
  value       = module.network.private_subnet_ids
}

output "nat_public_ip" {
  description = "Outbound IP of the private subnets (NAT gateway)."
  value       = module.network.nat_public_ip
}

output "ami_id" {
  description = "Ubuntu AMI used for the instances."
  value       = module.compute.ami_id
}

output "ssh_user" {
  description = "Login user for the Ubuntu AMI."
  value       = "ubuntu"
}

output "ssh_command" {
  description = "Ready-to-paste SSH command to the private app VM through the bastion."
  value       = "ssh -i ~/.ssh/sokosmart_f3 -J ubuntu@${module.compute.bastion_public_ip} ubuntu@${module.compute.app_private_ip}"
}

output "ecr_repository_url" {
  description = "Private registry URL for docker push and pull."
  value       = module.ecr.repository_url
}

output "db_endpoint" {
  description = "RDS host name. Reachable only from the app security group."
  value       = module.database.endpoint
}

output "db_port" {
  description = "RDS port."
  value       = module.database.port
}

output "db_name" {
  description = "Database name."
  value       = module.database.db_name
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret holding the database credentials."
  value       = module.database.secret_arn
}