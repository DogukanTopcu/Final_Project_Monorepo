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

variable "create_backend_resources" {
  type    = bool
  default = false
}
