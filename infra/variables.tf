variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "project" {
  description = "Project name, used to prefix all resources"
  type        = string
  default     = "sokosmart"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "Docker image for the price-service (overridden by CI once ECR push exists)"
  type        = string
  default     = "public.ecr.aws/docker/library/nginx:alpine"
}

variable "container_port" {
  description = "Port the Flask app listens on"
  type        = number
  default     = 5000
}

variable "desired_tasks" {
  description = "Number of Fargate tasks to run"
  type        = number
  default     = 2
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "plan_only" {
  description = "Skip AWS credential checks so `terraform plan` works without live credentials (set false to apply)"
  type        = bool
  default     = true
}
