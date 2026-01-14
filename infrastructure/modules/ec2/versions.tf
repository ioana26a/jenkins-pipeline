terraform {
  required_version = ">= 1.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }
  backend "s3" {
    bucket         = "ioana-bucket-06.11.2025"
    key            = "circle/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "ioana-project-state"
    encrypt        = true
  }
}
