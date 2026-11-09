output "instance_id" {
  description = "ID of the EC2 instance."
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "Public IPv4 address of the instance."
  value       = aws_instance.app.public_ip
}

output "public_dns" {
  description = "Public DNS name of the instance."
  value       = aws_instance.app.public_dns
}

output "private_ip" {
  description = "Private IP inside the VPC."
  value       = aws_instance.app.private_ip
}

output "ami_id" {
  description = "AMI the instance was launched from."
  value       = aws_instance.app.ami
}

output "key_name" {
  description = "Name of the EC2 key pair."
  value       = aws_key_pair.this.key_name
}
