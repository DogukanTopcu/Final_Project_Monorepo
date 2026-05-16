variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.medium"
}

variable "root_volume_size_gb" {
  type    = number
  default = 30
}

variable "root_volume_type" {
  type    = string
  default = "gp3"
}

variable "ami_id" {
  type    = string
  default = ""
}

variable "use_spot" {
  type    = bool
  default = false
}

variable "spot_price" {
  type    = string
  default = ""
}

variable "is_gpu" {
  type    = bool
  default = false
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "public_key_path" {
  type    = string
  default = "~/.ssh/thesis-key.pub"
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to SSH — never 0.0.0.0/0"

  validation {
    condition     = var.allowed_ssh_cidr != "0.0.0.0/32"
    error_message = "allowed_ssh_cidr must be your real public IP in CIDR form, not 0.0.0.0/32."
  }
}

variable "instance_profile_arn" {
  type = string
}

variable "ecr_repo_url" {
  type    = string
  default = ""
}

variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "container_image_uri" {
  type        = string
  description = "Full container image URI including tag"
}

variable "api_port" {
  type    = number
  default = 8000
}

variable "api_ingress_cidrs" {
  type    = list(string)
  default = []
}

variable "container_name" {
  type    = string
  default = "thesis-runner"
}

variable "port_mappings" {
  type    = list(string)
  default = []
}

variable "container_runtime_args" {
  type    = list(string)
  default = []
}

variable "container_command" {
  type    = string
  default = ""
}

variable "secret_names" {
  type    = list(string)
  default = []
}

variable "extra_env" {
  type    = map(string)
  default = {}
}
