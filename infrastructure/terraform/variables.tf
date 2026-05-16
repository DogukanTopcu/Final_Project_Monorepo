variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type    = string
  default = "dev"
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
