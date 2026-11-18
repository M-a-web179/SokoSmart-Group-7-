variable "name" {
  description = "Name prefix for the network resources."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "public_subnet_count" {
  description = "Number of public subnets (one per AZ). The same number of private subnets is created in the same AZs."
  type        = number
  default     = 2
}
