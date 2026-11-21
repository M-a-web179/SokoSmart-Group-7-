variable "name" {
  description = "Name prefix for the IAM resources."
  type        = string
}

variable "ecr_repository_name" {
  description = "Name of the private ECR repository the app VM may pull from."
  type        = string
}

variable "db_secret_arn" {
  description = "ARN of the Secrets Manager secret the app VM may read."
  type        = string
}