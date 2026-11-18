variable "name" {
  description = "Repository name."
  type        = string
}

variable "force_delete" {
  description = "Delete the repository even if it still holds images."
  type        = bool
  default     = true
}

variable "keep_images" {
  description = "How many images to keep."
  type        = number
  default     = 10
}