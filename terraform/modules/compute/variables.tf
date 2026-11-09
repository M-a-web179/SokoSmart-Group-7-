variable "name" {
  description = "Name prefix for the compute resources."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
}

variable "subnet_id" {
  description = "Subnet to launch the instance in."
  type        = string
}

variable "security_group_ids" {
  description = "Security groups to attach to the instance."
  type        = list(string)
}

variable "ssh_public_key" {
  description = "Contents of the SSH public key for the key pair."
  type        = string
}

variable "root_volume_size" {
  description = "Root volume size in GB."
  type        = number
  default     = 20
}

variable "instance_tags" {
  description = "Extra tags for the instance only."
  type        = map(string)
  default     = {}
}
