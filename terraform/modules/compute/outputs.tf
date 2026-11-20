# ---------------------------------------------------------------- bastion

output "bastion_instance_id" {
  description = "ID of the bastion host."
  value       = aws_instance.bastion.id
}

output "bastion_public_ip" {
  description = "Public IP of the bastion host. SSH lands here first."
  value       = aws_instance.bastion.public_ip
}

output "bastion_private_ip" {
  description = "Private IP of the bastion inside the VPC."
  value       = aws_instance.bastion.private_ip
}

# ---------------------------------------------------------------- app

output "app_instance_id" {
  description = "ID of the app VM."
  value       = aws_instance.app.id
}

output "app_private_ip" {
  description = "Private IP of the app VM. Reach it through the bastion."
  value       = aws_instance.app.private_ip
}

# ---------------------------------------------------------------- shared

output "ami_id" {
  description = "Ubuntu AMI the instances were launched from."
  value       = aws_instance.app.ami
}

output "key_name" {
  description = "Name of the EC2 key pair."
  value       = aws_key_pair.this.key_name
}
