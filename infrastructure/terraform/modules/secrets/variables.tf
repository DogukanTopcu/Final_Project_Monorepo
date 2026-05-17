variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type = string
}

variable "create_hosted_provider_secrets" {
  type        = bool
  description = "Whether to create optional hosted-provider API key secrets for Kimi/OpenAI-compatible gateways."
  default     = false
}

variable "create_hf_token_secret" {
  type        = bool
  description = "Whether to create the shared Hugging Face token secret or only reference an existing one."
  default     = true
}
