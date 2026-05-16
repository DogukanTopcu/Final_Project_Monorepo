variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "create_backend_lock_table" {
  type    = bool
  default = false
}
