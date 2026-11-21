variable "name" {
  description = "Name prefix for the security groups."
  type        = string
}

variable "vpc_id" {
  description = "VPC the security groups belong to."
  type        = string
}

variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to SSH to the bastion (port 22)."
  type        = list(string)
}

variable "app_allowed_cidrs" {
  description = "CIDR blocks allowed to reach public HTTP on the bastion."
  type        = list(string)
}

variable "app_port" {
  description = "Port the application listens on."
  type        = number
}

variable "db_port" {
  description = "Port the database listens on."
  type        = number
  default     = 5432
}