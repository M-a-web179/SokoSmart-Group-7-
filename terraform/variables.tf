# ---------------------------------------------------------------- general

variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "eu-west-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "aws_region must look like a region code, e.g. eu-west-1."
  }
}

variable "aws_profile" {
  description = "Named profile from ~/.aws/credentials. Leave null to use env vars or the default profile."
  type        = string
  default     = null
}

variable "project" {
  description = "Project name. Used as a prefix for resource names and in tags."
  type        = string
  default     = "sokosmart"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project))
    error_message = "project must be 3-21 chars: lowercase letters, numbers and dashes, starting with a letter."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "owner" {
  description = "Person or team responsible for these resources (goes in the Owner tag)."
  type        = string
  default     = "group-7"
}

variable "extra_tags" {
  description = "Any additional tags to put on every resource."
  type        = map(string)
  default     = {}
}

# ---------------------------------------------------------------- network

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "public_subnet_count" {
  description = "How many public subnets to create, each in its own availability zone."
  type        = number
  default     = 2

  validation {
    condition     = var.public_subnet_count >= 1 && var.public_subnet_count <= 3
    error_message = "public_subnet_count must be between 1 and 3."
  }
}

# ---------------------------------------------------------------- security

variable "ssh_allowed_cidrs" {
  description = "Who can SSH in. Use your own public IP as a /32, never 0.0.0.0/0."
  type        = list(string)

  validation {
    condition     = length(var.ssh_allowed_cidrs) > 0 && alltrue([for c in var.ssh_allowed_cidrs : can(cidrhost(c, 0))])
    error_message = "ssh_allowed_cidrs must contain at least one valid CIDR block."
  }

  validation {
    condition     = !contains(var.ssh_allowed_cidrs, "0.0.0.0/0")
    error_message = "SSH must not be open to the whole internet (0.0.0.0/0)."
  }
}

variable "app_port" {
  description = "Port the price-service listens on (gunicorn in the Dockerfile)."
  type        = number
  default     = 5000

  validation {
    condition     = var.app_port > 0 && var.app_port < 65536
    error_message = "app_port must be between 1 and 65535."
  }
}

variable "app_allowed_cidrs" {
  description = "Who can reach the app and HTTP ports."
  type        = list(string)
  default     = ["0.0.0.0/0"]

  validation {
    condition     = alltrue([for c in var.app_allowed_cidrs : can(cidrhost(c, 0))])
    error_message = "app_allowed_cidrs must only contain valid CIDR blocks."
  }
}

# ---------------------------------------------------------------- compute

variable "instance_type" {
  description = "EC2 instance size. Kept to free-tier sizes."
  type        = string
  default     = "t3.micro"

  validation {
    condition     = contains(["t2.micro", "t3.micro", "t3.small"], var.instance_type)
    error_message = "instance_type must be t2.micro, t3.micro or t3.small."
  }
}

variable "ssh_public_key_path" {
  description = "Path to the public key that gets loaded into the EC2 key pair."
  type        = string
  default     = "~/.ssh/sokosmart_f3.pub"
}

variable "root_volume_size" {
  description = "Root disk size in GB."
  type        = number
  default     = 20

  validation {
    condition     = var.root_volume_size >= 8 && var.root_volume_size <= 30
    error_message = "root_volume_size must be 8-30 GB (30 is the free tier limit)."
  }
}
