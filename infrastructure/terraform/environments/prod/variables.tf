variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "aws_region" {
  type    = string
  default = "eu-central-1"
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

variable "cpu_instance_type" {
  type    = string
  default = "t3.large"
}

variable "public_api_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "enabled_vllm_models" {
  type        = set(string)
  description = "Selected models to self-host on dedicated GPU EC2 instances in prod."
  default     = []
}

variable "vllm_instance_type_overrides" {
  type        = map(string)
  description = "Optional per-model EC2 instance type overrides for self-hosted vLLM models."
  default     = {}
}

variable "vllm_container_image" {
  type        = string
  description = "Pinned vLLM OpenAI-compatible container image."
  default     = "vllm/vllm-openai:v0.19.1"
}
