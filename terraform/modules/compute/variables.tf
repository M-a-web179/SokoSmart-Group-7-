variable "name" {
  description = "Name prefix for the compute resources."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for the app VM."
  type        = string
}

variable "bastion_instance_type" {
  description = "EC2 instance type for the bastion host. It only forwards SSH, so the smallest size is enough."
  type        = string
  default     = "t3.micro"
}

variable "app_subnet_id" {
  description = "Private subnet to launch the app VM in."
  type        = string
}

variable "bastion_subnet_id" {
  description = "Public subnet to launch the bastion host in."
  type        = string
}

variable "app_security_group_ids" {
  description = "Security groups for the app VM (SSH only from the bastion, app port from the web)."
  type        = list(string)
}

variable "bastion_security_group_ids" {
  description = "Security groups for the bastion host (SSH from admin IPs only)."
  type        = list(string)
}

variable "ssh_public_key" {
  description = "Contents of the SSH public key for the key pair (used by both instances)."
  type        = string
}

variable "root_volume_size" {
  description = "Root volume size in GB for the app VM."
  type        = number
  default     = 20
}

variable "instance_tags" {
  description = "Extra tags for both instances."
  type        = map(string)
  default     = {}
}
