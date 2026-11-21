output "instance_profile_name" {
  description = "Instance profile to attach to the app VM."
  value       = aws_iam_instance_profile.app.name
}

output "role_arn" {
  description = "ARN of the app VM role."
  value       = aws_iam_role.app.arn
}