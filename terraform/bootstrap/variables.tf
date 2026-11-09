variable "aws_region" {
  description = "Region for the state bucket."
  type        = string
  default     = "eu-west-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use. Null means env vars / default profile."
  type        = string
  default     = null
}

variable "project" {
  description = "Used in the bucket name and tags."
  type        = string
  default     = "sokosmart"
}

variable "force_destroy" {
  description = "Allow destroying the bucket even when it still has state files in it."
  type        = bool
  default     = false
}
