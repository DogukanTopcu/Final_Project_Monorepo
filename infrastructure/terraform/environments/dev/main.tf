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
  nat_enabled = false
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

module "ec2" {
  source                = "../../modules/ec2"
  project               = var.project
  environment           = var.environment
  gcp_project_id        = var.gcp_project_id
  gcp_region            = var.gcp_region
  gcp_zone              = var.gcp_zone
  vpc_id                = module.vpc.vpc_id
  vpc_cidr              = module.vpc.vpc_cidr
  subnet_id             = module.vpc.public_subnet_ids[0]
  instance_type         = "e2-standard-4"
  root_volume_size_gb   = 40
  instance_count        = 1
  use_spot              = false
  is_gpu                = false
  allowed_ssh_cidr      = var.allowed_ssh_cidr
  public_key_path       = var.public_key_path
  service_account_email = module.iam.ec2_runner_instance_profile_arn
  artifact_registry_host = module.ecr.registry_host
  container_image_uri   = "${module.ecr.runner_repo_url}:latest"
  container_name        = "thesis-runner"
  container_command     = "sleep infinity"
  secret_names = [
    module.secrets.kimi_key_name,
    module.secrets.openai_compatible_key_name,
    module.secrets.hf_token_name,
  ]
  depends_on = [google_project_service.required]
}

module "cloudwatch" {
  source         = "../../modules/cloudwatch"
  project        = var.project
  environment    = var.environment
  gcp_project_id = var.gcp_project_id
  gcp_region     = var.gcp_region
  alert_email    = var.alert_email
  cost_threshold = 50
  instance_ids   = module.ec2.instance_ids
  results_bucket = module.s3.results_bucket_name
  dynamodb_table = module.dynamodb.experiments_table_name
  depends_on     = [google_project_service.required]
}

output "runner_public_ip" {
  value = try(module.ec2.public_ips[0], null)
}

output "runner_private_ip" {
  value = try(module.ec2.private_ips[0], null)
}
