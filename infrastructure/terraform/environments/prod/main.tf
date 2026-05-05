module "vpc" {
  source      = "../../modules/vpc"
  project     = var.project
  environment = var.environment
  nat_enabled = true
}

module "s3" {
  source      = "../../modules/s3"
  project     = var.project
  environment = var.environment
}

module "ecr" {
  source      = "../../modules/ecr"
  project     = var.project
  environment = var.environment
}

module "dynamodb" {
  source      = "../../modules/dynamodb"
  project     = var.project
  environment = var.environment
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

module "ec2_gpu" {
  source               = "../../modules/ec2"
  project              = var.project
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = module.vpc.vpc_cidr
  subnet_id            = module.vpc.private_subnet_ids[0]
  instance_type        = "g4dn.xlarge"
  instance_count       = 1
  use_spot             = true
  spot_price           = "0.50"
  is_gpu               = true
  allowed_ssh_cidr     = var.allowed_ssh_cidr
  public_key_path      = var.public_key_path
  instance_profile_arn = module.iam.ec2_runner_instance_profile_arn
  ecr_repo_url         = module.ecr.runner_repo_url
  aws_region           = var.aws_region
}

module "ec2_cpu" {
  source               = "../../modules/ec2"
  project              = var.project
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  vpc_cidr             = module.vpc.vpc_cidr
  subnet_id            = module.vpc.public_subnet_ids[0]
  instance_type        = "t3.large"
  instance_count       = 1
  use_spot             = false
  is_gpu               = false
  allowed_ssh_cidr     = var.allowed_ssh_cidr
  public_key_path      = var.public_key_path
  instance_profile_arn = module.iam.ec2_runner_instance_profile_arn
  ecr_repo_url         = module.ecr.api_repo_url
  aws_region           = var.aws_region
}

module "cloudwatch" {
  source         = "../../modules/cloudwatch"
  project        = var.project
  environment    = var.environment
  aws_region     = var.aws_region
  alert_email    = var.alert_email
  cost_threshold = 50
  instance_ids   = concat(module.ec2_gpu.instance_ids, module.ec2_cpu.instance_ids)
  results_bucket = module.s3.results_bucket_name
  dynamodb_table = module.dynamodb.experiments_table_name
}
