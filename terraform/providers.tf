provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  # Every resource gets these tags, so we can see what belongs to the
  # project in the console and in the billing report.
  default_tags {
    tags = local.common_tags
  }
}
