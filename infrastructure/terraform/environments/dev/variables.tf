variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR block allowed to SSH into instances"
}

variable "public_key_path" {
  type    = string
  default = "~/.ssh/thesis-key.pub"
}

variable "alert_email" {
  type    = string
  default = ""
}

variable "github_repo" {
  type        = string
  description = "GitHub repo in format owner/repo"
  default     = "*"
}
