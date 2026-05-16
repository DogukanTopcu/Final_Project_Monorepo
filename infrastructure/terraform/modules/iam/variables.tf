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

variable "github_repo" {
  type        = string
  description = "GitHub repo in format owner/repo"
  default     = "*"
}

variable "create_github_oidc" {
  type    = bool
  default = true
}
