terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

locals {
  required_services = toset([
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
    "sts.googleapis.com",
  ])
}

resource "google_project_service" "required" {
  for_each = local.required_services

  project            = var.gcp_project_id
  service            = each.value
  disable_on_destroy = false
}

module "vpc" {
  source      = "../../modules/vpc"
  project     = var.project
  environment = var.environment
  gcp_region  = var.gcp_region
  nat_enabled = true
  depends_on  = [google_project_service.required]
}

module "s3" {
  source                   = "../../modules/s3"
  project                  = var.project
  environment              = var.environment
  gcp_project_id           = var.gcp_project_id
  gcp_region               = var.gcp_region
  create_backend_resources = false
  depends_on               = [google_project_service.required]
}

module "ecr" {
  source         = "../../modules/ecr"
  project        = var.project
  environment    = var.environment
  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region
  depends_on     = [google_project_service.required]
}

module "dynamodb" {
  source                    = "../../modules/dynamodb"
  project                   = var.project
  environment               = var.environment
  create_backend_lock_table = false
  depends_on                = [google_project_service.required]
}

module "secrets" {
  source      = "../../modules/secrets"
  project     = var.project
  environment = var.environment
  depends_on  = [google_project_service.required]
}

module "iam" {
  source             = "../../modules/iam"
  project            = var.project
  environment        = var.environment
  gcp_project_id     = var.gcp_project_id
  github_repo        = var.github_repo
  create_github_oidc = true
  depends_on         = [google_project_service.required]
}

locals {
  secret_names = [
    module.secrets.kimi_key_name,
    module.secrets.openai_compatible_key_name,
    module.secrets.hf_token_name,
  ]

  vllm_model_deployments = {
    "llama3.3-70b" = {
      instance_type       = "a2-ultragpu-2g"
      root_volume_size_gb = 500
      runtime_args        = ["--ipc=host", "--shm-size=32g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model meta-llama/Llama-3.3-70B-Instruct --served-model-name meta-llama/Llama-3.3-70B-Instruct --port 8000 --tensor-parallel-size 2 --max-model-len 32768 --gpu-memory-utilization 0.92"
      api_port            = 8000
    }
    "qwen3.5-4b" = {
      instance_type       = "g2-standard-24"
      root_volume_size_gb = 150
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-4B --served-model-name Qwen/Qwen3.5-4B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.80"
      api_port            = 8000
    }
    "gemma4-4b" = {
      instance_type       = "g2-standard-24"
      root_volume_size_gb = 150
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model google/gemma-4-E4B-it --served-model-name google/gemma-4-E4B-it --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.80"
      api_port            = 8000
    }
    "llama3.2-3b" = {
      instance_type       = "g2-standard-24"
      root_volume_size_gb = 150
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model meta-llama/Llama-3.2-3B-Instruct --served-model-name meta-llama/Llama-3.2-3B-Instruct --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.75"
      api_port            = 8000
    }
    "qwen3.5-27b" = {
      instance_type       = "a2-ultragpu-1g"
      root_volume_size_gb = 250
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-27B --served-model-name Qwen/Qwen3.5-27B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.90"
      api_port            = 8000
    }
    "gpt-oss-20b" = {
      instance_type       = "g2-standard-24"
      root_volume_size_gb = 150
      runtime_args        = ["--ipc=host", "--shm-size=16g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model openai/gpt-oss-20b --served-model-name openai/gpt-oss-20b --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.88"
      api_port            = 8000
    }
    "gemma4-31b" = {
      instance_type       = "a2-ultragpu-1g"
      root_volume_size_gb = 250
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model nvidia/Gemma-4-31B-IT-NVFP4 --served-model-name nvidia/Gemma-4-31B-IT-NVFP4 --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.90"
      api_port            = 8000
    }
    "qwen3.5-35b-a3b" = {
      instance_type       = "a2-ultragpu-1g"
      root_volume_size_gb = 250
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-35B-A3B --served-model-name Qwen/Qwen3.5-35B-A3B --port 8000 --max-model-len 32768 --gpu-memory-utilization 0.90"
      api_port            = 8000
    }
    "gemma4-26b-a4b" = {
      instance_type       = "a2-ultragpu-1g"
      root_volume_size_gb = 250
      runtime_args        = ["--ipc=host", "--shm-size=24g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model nvidia/Gemma-4-26B-A4B-NVFP4 --served-model-name nvidia/Gemma-4-26B-A4B-NVFP4 --port 8000 --reasoning-parser gemma4 --max-model-len 32768 --gpu-memory-utilization 0.90"
      api_port            = 8000
    }
    "qwen3.5-122b-a10b" = {
      instance_type       = "a3-ultragpu-8g"
      root_volume_size_gb = 1200
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-122B-A10B --served-model-name Qwen/Qwen3.5-122B-A10B --port 8000 --tensor-parallel-size 8 --max-model-len 32768 --reasoning-parser qwen3 --language-model-only"
      api_port            = 8000
    }
    "kimi-k2.6-1t" = {
      instance_type       = "a3-ultragpu-8g"
      root_volume_size_gb = 2000
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model moonshotai/Kimi-K2.6 --served-model-name moonshotai/Kimi-K2.6 --port 8000 --tensor-parallel-size 8 --mm-encoder-tp-mode data --trust-remote-code --tool-call-parser kimi_k2 --reasoning-parser kimi_k2"
      api_port            = 8000
    }
    "qwen3.5-397b-a17b" = {
      instance_type       = "a3-ultragpu-8g"
      root_volume_size_gb = 2000
      runtime_args        = ["--ipc=host", "--shm-size=64g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model Qwen/Qwen3.5-397B-A17B --served-model-name Qwen/Qwen3.5-397B-A17B --port 8000 --tensor-parallel-size 8 --max-model-len 32768 --reasoning-parser qwen3 --language-model-only"
      api_port            = 8000
    }
    "gpt-oss-120b" = {
      instance_type       = "a2-ultragpu-4g"
      root_volume_size_gb = 800
      runtime_args        = ["--ipc=host", "--shm-size=48g", "-v /opt/hf-cache:/root/.cache/huggingface"]
      command             = "--model openai/gpt-oss-120b --served-model-name openai/gpt-oss-120b --port 8000 --tensor-parallel-size 4 --max-model-len 32768 --gpu-memory-utilization 0.92"
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
      THESIS_GCP_PROJECT_ID         = var.gcp_project_id
      THESIS_GCP_REGION             = var.gcp_region
      THESIS_GCS_RESULTS_BUCKET     = module.s3.results_bucket_name
      THESIS_GCS_ARTIFACTS_BUCKET   = module.s3.artifacts_bucket_name
      THESIS_FIRESTORE_COLLECTION   = module.dynamodb.experiments_table_name
      THESIS_ENVIRONMENT            = var.environment
      THESIS_MLFLOW_TRACKING_URI    = "http://localhost:5000"
      THESIS_BILLING_EXPORT_TABLE   = var.billing_export_table
      MLFLOW_TRACKING_URI           = "http://localhost:5000"
      THESIS_FORCE_VLLM             = length(var.enabled_vllm_models) > 0 ? "1" : "0"
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
  gcp_project_id         = var.gcp_project_id
  gcp_region             = var.gcp_region
  gcp_zone               = var.gpu_zone
  vpc_id                 = module.vpc.vpc_id
  vpc_cidr               = module.vpc.vpc_cidr
  subnet_id              = module.vpc.private_subnet_ids[0]
  instance_type          = each.value.instance_type
  root_volume_size_gb    = each.value.root_volume_size_gb
  instance_count         = 1
  use_spot               = false
  is_gpu                 = true
  allowed_ssh_cidr       = var.allowed_ssh_cidr
  public_key_path        = var.public_key_path
  service_account_email  = module.iam.ec2_runner_instance_profile_arn
  artifact_registry_host = module.ecr.registry_host
  api_port               = each.value.api_port
  api_ingress_cidrs      = [module.vpc.vpc_cidr]
  container_image_uri    = var.vllm_container_image
  container_name         = replace("vllm-${each.key}", ".", "-")
  port_mappings          = ["8000:8000"]
  container_runtime_args = each.value.runtime_args
  container_command      = each.value.command
  secret_names           = local.secret_names
  assign_public_ip       = false
  depends_on             = [google_project_service.required]
}

module "ec2_cpu" {
  source                = "../../modules/ec2"
  project               = var.project
  environment           = var.environment
  gcp_project_id        = var.gcp_project_id
  gcp_region            = var.gcp_region
  gcp_zone              = var.cpu_zone
  vpc_id                = module.vpc.vpc_id
  vpc_cidr              = module.vpc.vpc_cidr
  subnet_id             = module.vpc.public_subnet_ids[0]
  instance_type         = var.cpu_instance_type
  root_volume_size_gb   = 60
  instance_count        = 1
  use_spot              = false
  is_gpu                = false
  allowed_ssh_cidr      = var.allowed_ssh_cidr
  public_key_path       = var.public_key_path
  service_account_email = module.iam.ec2_runner_instance_profile_arn
  artifact_registry_host = module.ecr.registry_host
  api_port              = 8000
  api_ingress_cidrs     = var.public_api_cidrs
  container_image_uri   = "${module.ecr.api_repo_url}:latest"
  container_name        = "thesis-api"
  port_mappings         = ["8000:8000"]
  secret_names          = local.secret_names
  extra_env             = local.cpu_extra_env
  depends_on            = [google_project_service.required]
}

module "cloudwatch" {
  source         = "../../modules/cloudwatch"
  project        = var.project
  environment    = var.environment
  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region
  alert_email    = var.alert_email
  cost_threshold = 50
  instance_ids   = concat(flatten([for host in values(module.vllm_hosts) : host.instance_ids]), module.ec2_cpu.instance_ids)
  results_bucket = module.s3.results_bucket_name
  dynamodb_table = module.dynamodb.experiments_table_name
  depends_on     = [google_project_service.required]
}
