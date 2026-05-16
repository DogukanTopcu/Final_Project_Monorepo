project           = "thesis"
environment       = "prod"
aws_region        = "eu-central-1"
allowed_ssh_cidr  = "88.230.165.100/32"
public_key_path   = "~/.ssh/thesis-key.pub"
alert_email       = ""
github_repo       = "*"
cpu_instance_type = "t3.large"

# Keep this empty by default to avoid accidentally launching very expensive GPU hosts.
# Enable only the models you want to benchmark in that window.
enabled_vllm_models = ["gpt-oss-20b", "llama3.3-70b"]

# Examples:
# enabled_vllm_models = ["llama3.3-70b", "gpt-oss-20b"]
# enabled_vllm_models = ["gpt-oss-120b"]
# enabled_vllm_models = ["qwen3.5-397b-a17b"]
