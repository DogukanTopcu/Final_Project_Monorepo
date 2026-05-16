variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "create_backend_resources" {
  type    = bool
  default = false
}
