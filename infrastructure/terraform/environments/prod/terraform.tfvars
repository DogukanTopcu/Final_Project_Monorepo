project           = "thesis"
environment       = "prod"
gcp_project_id    = "llm-slm-comparison"
gcp_region        = "europe-west4"
gcp_zone          = "europe-west4-a"
cpu_zone          = "europe-west4-a"
gpu_zone          = "europe-west4-a"
allowed_ssh_cidr  = "88.230.165.100/32"
public_key_path   = "~/.ssh/thesis-key.pub"
alert_email       = ""
github_repo       = "*"
cpu_instance_type = "e2-standard-8"

# Keep this empty by default to avoid accidentally launching very expensive GPU hosts.
# Enable only the models you want to benchmark in that window.
enabled_vllm_models = ["qwen3.5-4b", "gpt-oss-20b"]

# Examples:
# enabled_vllm_models = ["llama3.3-70b", "gpt-oss-20b"]
# enabled_vllm_models = ["gpt-oss-120b"]
# enabled_vllm_models = ["llama3.3-70b", "gemma4-31b"]
