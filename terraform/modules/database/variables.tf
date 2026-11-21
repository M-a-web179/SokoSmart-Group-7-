variable "name" {
  description = "Name prefix."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnets in at least two AZs."
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) >= 2
    error_message = "RDS needs subnets in at least two availability zones."
  }
}

variable "db_security_group_id" {
  description = "Security group that only allows the app VM to connect."
  type        = string
}

variable "db_name" {
  description = "Initial database name."
  type        = string
  default     = "sokosmart"
}

variable "db_username" {
  description = "Master username."
  type        = string
  default     = "sokosmart_app"
}

variable "engine_version" {
  description = "PostgreSQL major version."
  type        = string
  default     = "16"
}

variable "instance_class" {
  description = "RDS instance size."
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Storage in GB."
  type        = number
  default     = 20
}