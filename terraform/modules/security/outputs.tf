output "bastion_sg_id" {
  description = "ID of the bastion security group."
  value       = aws_security_group.bastion.id
}

output "app_sg_id" {
  description = "ID of the app VM security group."
  value       = aws_security_group.app.id
}

output "db_sg_id" {
  description = "ID of the database security group."
  value       = aws_security_group.db.id
}

output "security_group_id" {
  description = "Alias of app_sg_id, kept until the compute wiring is updated."
  value       = aws_security_group.app.id
}

output "ingress_rule_keys" {
  description = "Which bastion ingress rules were created (port-cidr)."
  value       = keys(aws_vpc_security_group_ingress_rule.bastion)
}