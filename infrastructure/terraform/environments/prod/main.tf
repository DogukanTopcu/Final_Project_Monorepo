module "vpc" {
  source      = "../../modules/vpc"
  project     = var.project
  environment = var.environment
  nat_enabled = true
}

module "s3" {
  source                   = "../../modules/s3"
  project                  = var.project
  environment              = var.environment
  create_backend_resources = false
}

module "ecr" {
  source      = "../../modules/ecr"
  project     = var.project
  environment = var.environment
}

module "dynamodb" {
  source                    = "../../modules/dynamodb"
  project                   = var.project
  environment               = var.environment
  create_backend_lock_table = false
}

module "secrets" {
  source      = "../../modules/secrets"
  project     = var.project
  environment = var.environment
}

module "iam" {
  source             = "../../modules/iam"
  project            = var.project
  environment        = var.environment
  github_repo        = var.github_repo
  create_github_oidc = true
}

locals {
  secret_names = [
    module.secrets.kimi_key_name,
    module.secrets.openai_compatible_key_name,
    module.secrets.hf_token_name,
  ]

  vllm_model_deployments = {
    "llama3.3-70b" = {
      instance_type       = "g6e.12xlarge"
      root_volume_size_gb = 300
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=32g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model meta-llama/Llama-3.3-70B-Instruct --served-model-name meta-llama/Llama-3.3-70B-Instruct --port 8000 --tensor-parallel-size 4 --max-model-len 32768 --gpu-memory-utilization 0.92"
      endpoint_env        = "VLLM_LLAMA33_70B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "qwen3.5-4b" = {
      instance_type       = "g5.2xlarge"
      root_volume_size_gb = 100
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-4B --served-model-name Qwen/Qwen3.5-4B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.75"
      endpoint_env        = "VLLM_QWEN35_4B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "gemma4-4b" = {
      instance_type       = "g5.2xlarge"
      root_volume_size_gb = 100
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model google/gemma-4-E4B-it --served-model-name google/gemma-4-E4B-it --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.75"
      endpoint_env        = "VLLM_GEMMA4_E4B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "llama3.2-3b" = {
      instance_type       = "g5.2xlarge"
      root_volume_size_gb = 100
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model meta-llama/Llama-3.2-3B-Instruct --served-model-name meta-llama/Llama-3.2-3B-Instruct --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.70"
      endpoint_env        = "VLLM_LLAMA32_3B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "qwen3.5-27b" = {
      instance_type       = "g6e.4xlarge"
      root_volume_size_gb = 200
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-27B --served-model-name Qwen/Qwen3.5-27B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.88"
      endpoint_env        = "VLLM_QWEN35_27B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "gpt-oss-20b" = {
      instance_type       = "g5.2xlarge"
      root_volume_size_gb = 150
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model openai/gpt-oss-20b --served-model-name openai/gpt-oss-20b --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.88"
      endpoint_env        = "VLLM_GPT_OSS_20B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "gemma4-31b" = {
      instance_type       = "g6e.4xlarge"
      root_volume_size_gb = 200
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model nvidia/Gemma-4-31B-IT-NVFP4 --served-model-name nvidia/Gemma-4-31B-IT-NVFP4 --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.90"
      endpoint_env        = "VLLM_GEMMA4_31B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "qwen3.5-35b-a3b" = {
      instance_type       = "g6e.4xlarge"
      root_volume_size_gb = 200
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-35B-A3B --served-model-name Qwen/Qwen3.5-35B-A3B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.90"
      endpoint_env        = "VLLM_QWEN35_35B_A3B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "gemma4-26b-a4b" = {
      instance_type       = "g6e.4xlarge"
      root_volume_size_gb = 200
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model nvidia/Gemma-4-26B-A4B-NVFP4 --served-model-name nvidia/Gemma-4-26B-A4B-NVFP4 --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.88"
      endpoint_env        = "VLLM_GEMMA4_26B_A4B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "qwen3.5-122b-a10b" = {
      instance_type       = "g6e.48xlarge"
      root_volume_size_gb = 800
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-122B-A10B --served-model-name Qwen/Qwen3.5-122B-A10B --port 8000 --tensor-parallel-size 8 --max-model-len 32768 --reasoning-parser qwen3 --language-model-only"
      endpoint_env        = "VLLM_QWEN35_122B_A10B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "kimi-k2.6-1t" = {
      instance_type       = "p5e.48xlarge"
      root_volume_size_gb = 2000
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model moonshotai/Kimi-K2.6 --served-model-name moonshotai/Kimi-K2.6 --port 8000 --tensor-parallel-size 8 --mm-encoder-tp-mode data --trust-remote-code --tool-call-parser kimi_k2 --reasoning-parser kimi_k2"
      endpoint_env        = "VLLM_KIMI_K26_1T_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "qwen3.5-397b-a17b" = {
      instance_type       = "p5e.48xlarge"
      root_volume_size_gb = 2000
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-397B-A17B --served-model-name Qwen/Qwen3.5-397B-A17B --port 8000 --tensor-parallel-size 8 --max-model-len 32768 --reasoning-parser qwen3 --language-model-only"
      endpoint_env        = "VLLM_QWEN35_397B_A17B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
    "gpt-oss-120b" = {
      instance_type       = "p5.4xlarge"
      root_volume_size_gb = 500
      use_spot            = false
      spot_price          = ""
      runtime_args        = ["--ipc=host", "--shm-size=32g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model openai/gpt-oss-120b --served-model-name openai/gpt-oss-120b --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.92"
      endpoint_env        = "VLLM_GPT_OSS_120B_URL"
      endpoint_path       = "/v1"
      api_port            = 8000
    }
  }

  selected_vllm_deployments = {
    for model_id, deployment in local.vllm_model_deployments :
    model_id => merge(deployment, {
      instance_type = lookup(var.vllm_instance_type_overrides, model_id, deployment.instance_type)
    })
    if contains(var.enabled_vllm_models, model_id)
  }

  cpu_extra_env = merge(
    {
      THESIS_AWS_REGION          = var.aws_region
      THESIS_S3_RESULTS_BUCKET   = module.s3.results_bucket_name
      THESIS_S3_ARTIFACTS_BUCKET = module.s3.artifacts_bucket_name
      THESIS_DYNAMODB_TABLE      = module.dynamodb.experiments_table_name
      THESIS_ENVIRONMENT         = var.environment
      THESIS_MLFLOW_TRACKING_URI = "http://localhost:5000"
      MLFLOW_TRACKING_URI        = "http://localhost:5000"
      THESIS_FORCE_VLLM          = length(var.enabled_vllm_models) > 0 ? "1" : "0"
    },
    contains(var.enabled_vllm_models, "llama3.3-70b") ? {
      VLLM_LLAMA33_70B_URL = "http://${module.vllm_hosts["llama3.3-70b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "qwen3.5-4b") ? {
      VLLM_QWEN35_4B_URL = "http://${module.vllm_hosts["qwen3.5-4b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "gemma4-4b") ? {
      VLLM_GEMMA4_E4B_URL = "http://${module.vllm_hosts["gemma4-4b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "llama3.2-3b") ? {
      VLLM_LLAMA32_3B_URL = "http://${module.vllm_hosts["llama3.2-3b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "qwen3.5-27b") ? {
      VLLM_QWEN35_27B_URL = "http://${module.vllm_hosts["qwen3.5-27b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "gpt-oss-20b") ? {
      VLLM_GPT_OSS_20B_URL = "http://${module.vllm_hosts["gpt-oss-20b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "gemma4-31b") ? {
      VLLM_GEMMA4_31B_URL = "http://${module.vllm_hosts["gemma4-31b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "qwen3.5-35b-a3b") ? {
      VLLM_QWEN35_35B_A3B_URL = "http://${module.vllm_hosts["qwen3.5-35b-a3b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "gemma4-26b-a4b") ? {
      VLLM_GEMMA4_26B_A4B_URL = "http://${module.vllm_hosts["gemma4-26b-a4b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "qwen3.5-122b-a10b") ? {
      VLLM_QWEN35_122B_A10B_URL = "http://${module.vllm_hosts["qwen3.5-122b-a10b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "kimi-k2.6-1t") ? {
      VLLM_KIMI_K26_1T_URL = "http://${module.vllm_hosts["kimi-k2.6-1t"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "qwen3.5-397b-a17b") ? {
      VLLM_QWEN35_397B_A17B_URL = "http://${module.vllm_hosts["qwen3.5-397b-a17b"].private_ips[0]}:8000/v1"
    } : {},
    contains(var.enabled_vllm_models, "gpt-oss-120b") ? {
      VLLM_GPT_OSS_120B_URL = "http://${module.vllm_hosts["gpt-oss-120b"].private_ips[0]}:8000/v1"
    } : {},
  )
}

module "vllm_hosts" {
  for_each = local.selected_vllm_deployments

  source                 = "../../modules/ec2"
  project                = var.project
  environment            = "${var.environment}-${replace(each.key, ".", "-")}"
  vpc_id                 = module.vpc.vpc_id
  vpc_cidr               = module.vpc.vpc_cidr
  subnet_id              = module.vpc.private_subnet_ids[0]
  instance_type          = each.value.instance_type
  root_volume_size_gb    = each.value.root_volume_size_gb
  instance_count         = 1
  use_spot               = each.value.use_spot
  spot_price             = each.value.spot_price
  is_gpu                 = true
  allowed_ssh_cidr       = var.allowed_ssh_cidr
  public_key_path        = var.public_key_path
  instance_profile_arn   = module.iam.ec2_runner_instance_profile_arn
  ecr_repo_url           = ""
  aws_region             = var.aws_region
  api_port               = each.value.api_port
  api_ingress_cidrs      = [module.vpc.vpc_cidr]
  container_image_uri    = var.vllm_container_image
  container_name         = replace("vllm-${each.key}", ".", "-")
  port_mappings          = ["8000:8000"]
  container_runtime_args = each.value.runtime_args
  container_command      = each.value.command
  secret_names           = local.secret_names
}

module "ec2_cpu" {
  source               = "../../modules/ec2"
  project              = var.project
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = module.vpc.vpc_cidr
  subnet_id            = module.vpc.public_subnet_ids[0]
  instance_type        = var.cpu_instance_type
  root_volume_size_gb  = 40
  instance_count       = 1
  use_spot             = false
  is_gpu               = false
  allowed_ssh_cidr     = var.allowed_ssh_cidr
  public_key_path      = var.public_key_path
  instance_profile_arn = module.iam.ec2_runner_instance_profile_arn
  ecr_repo_url         = module.ecr.api_repo_url
  aws_region           = var.aws_region
  api_port             = 8000
  api_ingress_cidrs    = var.public_api_cidrs
  container_image_uri  = "${module.ecr.api_repo_url}:latest"
  container_name       = "thesis-api"
  port_mappings        = ["8000:8000"]
  secret_names         = local.secret_names
  extra_env            = local.cpu_extra_env
}

module "cloudwatch" {
  source         = "../../modules/cloudwatch"
  project        = var.project
  environment    = var.environment
  aws_region     = var.aws_region
  alert_email    = var.alert_email
  cost_threshold = 50
  instance_ids   = concat(flatten([for host in values(module.vllm_hosts) : host.instance_ids]), module.ec2_cpu.instance_ids)
  results_bucket = module.s3.results_bucket_name
  dynamodb_table = module.dynamodb.experiments_table_name
}
