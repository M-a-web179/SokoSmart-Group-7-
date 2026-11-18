output "endpoint" {
  description = "Database host name."
  value       = aws_db_instance.this.address
}

output "port" {
  description = "Database port."
  value       = aws_db_instance.this.port
}

output "db_name" {
  description = "Database name."
  value       = var.db_name
}

output "secret_arn" {
  description = "Secrets Manager secret holding the credentials."
  value       = aws_secretsmanager_secret.db.arn
}