output "instance_public_ip" {
  description = "Public IP of the app server. Use this in the Ansible inventory."
  value       = module.compute.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the app server."
  value       = module.compute.public_dns
}

output "instance_id" {
  description = "EC2 instance ID."
  value       = module.compute.instance_id
}

output "vpc_id" {
  description = "ID of the VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = module.network.public_subnet_ids
}

output "security_group_id" {
  description = "ID of the app server security group."
  value       = module.security.security_group_id
}

output "ami_id" {
  description = "Ubuntu AMI used for the instance."
  value       = module.compute.ami_id
}

output "ssh_user" {
  description = "Login user for the Ubuntu AMI."
  value       = "ubuntu"
}

output "ssh_command" {
  description = "Ready-to-paste SSH command (swap in your private key path)."
  value       = "ssh -i ~/.ssh/sokosmart_f3 ubuntu@${module.compute.public_ip}"
}

output "app_url" {
  description = "Where the price-service will answer once Ansible has deployed it."
  value       = "http://${module.compute.public_ip}:${var.app_port}/health"
}
