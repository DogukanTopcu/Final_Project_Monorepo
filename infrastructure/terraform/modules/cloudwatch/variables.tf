variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "alert_email" {
  type    = string
  default = ""
}

variable "cost_threshold" {
  type    = number
  default = 50
}

variable "instance_ids" {
  type    = list(string)
  default = []
}

variable "results_bucket" {
  type    = string
  default = ""
}

variable "dynamodb_table" {
  type    = string
  default = "thesis-experiments"
}
