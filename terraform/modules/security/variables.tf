variable "name" {
  description = "Name prefix for the security group."
  type        = string
}

variable "vpc_id" {
  description = "VPC the security group belongs to."
  type        = string
}

variable "ssh_allowed_cidrs" {
  description = "CIDR blocks allowed to SSH (port 22)."
  type        = list(string)
}

variable "app_allowed_cidrs" {
  description = "CIDR blocks allowed to reach HTTP and the app port."
  type        = list(string)
}

variable "app_port" {
  description = "Port the application listens on."
  type        = number
}
