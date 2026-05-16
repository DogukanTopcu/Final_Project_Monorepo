.PHONY: dev dev-down tf-init tf-plan tf-apply tf-destroy gar-login push-api push-runner mlflow-ui web

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
# Docker / Artifact Registry
# ──────────────────────────────────────────────

GCP_REGION ?= europe-west4
GCP_PROJECT_ID ?= thesis-gcp
GAR_HOST ?= $(GCP_REGION)-docker.pkg.dev
API_IMAGE ?= $(GAR_HOST)/$(GCP_PROJECT_ID)/thesis-api/thesis-api
RUNNER_IMAGE ?= $(GAR_HOST)/$(GCP_PROJECT_ID)/thesis-runner/thesis-runner

gar-login:
	gcloud auth configure-docker $(GAR_HOST) --quiet

push-api: gar-login
	docker buildx build --platform linux/amd64 -f docker/Dockerfile.api -t $(API_IMAGE):latest --push .

push-runner: gar-login
	docker buildx build --platform linux/amd64 -f docker/Dockerfile.runner -t $(RUNNER_IMAGE):latest --push .

# ──────────────────────────────────────────────
# Convenience
# ──────────────────────────────────────────────

mlflow-ui:
	open http://localhost:5000

web:
	open http://localhost:3000
