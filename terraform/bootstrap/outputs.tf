output "state_bucket" {
  description = "Put this in ../backend.hcl as the bucket value."
  value       = aws_s3_bucket.state.bucket
}

output "backend_hcl" {
  description = "Contents for ../backend.hcl"
  value       = <<-EOT
    bucket = "${aws_s3_bucket.state.bucket}"
    key    = "f3/dev/terraform.tfstate"
    region = "${var.aws_region}"
  EOT
}
