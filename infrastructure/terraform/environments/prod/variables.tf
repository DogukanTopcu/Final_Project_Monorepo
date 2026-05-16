variable "project" {
  type    = string
  default = "thesis"
}

variable "environment" {
  type    = string
  default = "prod"
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

variable "cpu_zone" {
  type    = string
  default = "europe-west4-a"
}

variable "gpu_zone" {
  type    = string
  default = "europe-west4-a"
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
  default = "e2-standard-8"
}

variable "public_api_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "enabled_vllm_models" {
  type        = set(string)
  description = "Selected models to self-host on dedicated GPU GCE instances in prod."
  default     = []
}

variable "vllm_instance_type_overrides" {
  type        = map(string)
  description = "Optional per-model GCE machine type overrides for self-hosted vLLM models."
  default     = {}
}

variable "vllm_container_image" {
  type        = string
  description = "Pinned vLLM OpenAI-compatible container image."
  default     = "vllm/vllm-openai:v0.19.1"
}

variable "billing_export_table" {
  type        = string
  description = "Optional BigQuery billing export table in project.dataset.table format."
  default     = ""
}
