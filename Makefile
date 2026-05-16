.PHONY: dev dev-down tf-init tf-plan tf-apply tf-destroy ecr-login push-api push-runner mlflow-ui web

# ──────────────────────────────────────────────
# Local development
# ──────────────────────────────────────────────

dev:
	cd docker && docker compose up --build

dev-down:
	cd docker && docker compose down -v

# ──────────────────────────────────────────────
# Terraform
# ──────────────────────────────────────────────

TF_DIR = infrastructure/terraform/environments/dev

tf-init:
	cd $(TF_DIR) && terraform init

tf-plan:
	cd $(TF_DIR) && terraform plan

tf-apply:
	cd $(TF_DIR) && terraform apply

tf-destroy:
	@echo "⚠️  WARNING: This will destroy ALL infrastructure in dev!"
	@echo "Press Ctrl+C to abort, or Enter to continue..."
	@read _confirm
	cd $(TF_DIR) && terraform destroy

# ──────────────────────────────────────────────
# Docker / ECR
# ──────────────────────────────────────────────

AWS_REGION ?= eu-central-1
ECR_REGISTRY ?= $(shell aws sts get-caller-identity --query Account --output text).dkr.ecr.$(AWS_REGION).amazonaws.com

ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)

push-api: ecr-login
	docker build -f docker/Dockerfile.api -t $(ECR_REGISTRY)/thesis-api:latest .
	docker push $(ECR_REGISTRY)/thesis-api:latest

push-runner: ecr-login
	docker build -f docker/Dockerfile.runner -t $(ECR_REGISTRY)/thesis-runner:latest .
	docker push $(ECR_REGISTRY)/thesis-runner:latest

# ──────────────────────────────────────────────
# Convenience
# ──────────────────────────────────────────────

mlflow-ui:
	open http://localhost:5000

web:
	open http://localhost:3000
