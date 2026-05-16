variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "gcp_project_id" {
  type = string
}

variable "gcp_region" {
  type    = string
  default = "europe-west4"
}

variable "gcp_zone" {
  type    = string
  default = "europe-west4-a"
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
  default = "e2-standard-4"
}

variable "root_volume_size_gb" {
  type    = number
  default = 30
}

variable "root_volume_type" {
  type    = string
  default = "pd-balanced"
}

variable "use_spot" {
  type    = bool
  default = false
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

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to SSH into instances"
}

variable "service_account_email" {
  type = string
}

variable "artifact_registry_host" {
  type    = string
  default = "europe-west4-docker.pkg.dev"
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

variable "assign_public_ip" {
  type    = bool
  default = true
}

variable "cpu_source_image_project" {
  type    = string
  default = "ubuntu-os-cloud"
}

variable "cpu_source_image_family" {
  type    = string
  default = "ubuntu-2204-lts"
}

variable "gpu_source_image_project" {
  type    = string
  default = "ml-images"
}

variable "gpu_source_image_family" {
  type    = string
  default = "common-cu128-ubuntu-2204-nvidia-570"
}
