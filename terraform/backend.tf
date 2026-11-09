# State lives in S3 so the team shares one copy instead of local files.
# The bucket is created once by ./bootstrap. Bucket name and key are passed
# at init time, because backend blocks can't read variables:
#
#   terraform init -backend-config=backend.hcl
#
# See backend.hcl.example.
terraform {
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
