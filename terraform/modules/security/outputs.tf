output "security_group_id" {
  description = "ID of the app server security group."
  value       = aws_security_group.app.id
}

output "ingress_rule_keys" {
  description = "Which ingress rules were created (port-cidr)."
  value       = keys(aws_vpc_security_group_ingress_rule.this)
}
