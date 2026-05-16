module "vpc" {
  source      = "../../modules/vpc"
  project     = var.project
  environment = var.environment
  nat_enabled = false
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

module "ec2" {
  source               = "../../modules/ec2"
  project              = var.project
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = module.vpc.vpc_cidr
  subnet_id            = module.vpc.public_subnet_ids[0]
  instance_type        = "t3.micro"
  root_volume_size_gb  = 30
  instance_count       = 1
  use_spot             = false
  is_gpu               = false
  allowed_ssh_cidr     = var.allowed_ssh_cidr
  public_key_path      = var.public_key_path
  instance_profile_arn = module.iam.ec2_runner_instance_profile_arn
  ecr_repo_url         = module.ecr.runner_repo_url
  aws_region           = var.aws_region
  container_image_uri  = "${module.ecr.runner_repo_url}:latest"
  container_name       = "thesis-runner"
  container_command    = "sleep infinity"
  secret_names = [
    module.secrets.kimi_key_name,
    module.secrets.openai_compatible_key_name,
    module.secrets.hf_token_name,
  ]
}

module "cloudwatch" {
  source         = "../../modules/cloudwatch"
  project        = var.project
  environment    = var.environment
  aws_region     = var.aws_region
  alert_email    = var.alert_email
  cost_threshold = 50
  instance_ids   = module.ec2.instance_ids
  results_bucket = module.s3.results_bucket_name
  dynamodb_table = module.dynamodb.experiments_table_name
}
