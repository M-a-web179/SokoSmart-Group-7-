terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state (enable once the team has an S3 bucket + DynamoDB lock table):
  # backend "s3" {
  #   bucket         = "sokosmart-tfstate"
  #   key            = "formative/terraform.tfstate"
  #   region         = "eu-west-1"
  #   dynamodb_table = "sokosmart-tflock"
  #   encrypt        = true
  # }
}
