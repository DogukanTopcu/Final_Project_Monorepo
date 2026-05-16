terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "s3" {
    bucket         = "thesis-tf-state"
    key            = "terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "thesis-tf-lock"
    encrypt        = true
  }
}
