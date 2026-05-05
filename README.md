# Thesis Experiment Platform — Monorepo

An end-to-end platform for running, tracking, and comparing SLM/LLM experiments across three architectures (Routing, Multi-Agent, Ensemble) with full AWS infrastructure and MLOps pipeline.

## Architecture Overview

```
Local Machine                          AWS Cloud
┌────────────────────┐                ┌─────────────────────────┐
│  Next.js Frontend  │───────────────▶│  EC2 (GPU) — runners    │
│  FastAPI Backend   │                │  EC2 (CPU) — API/MLflow │
│  ExperimentRunner  │                │  S3 — results/artifacts │
│  MLflow (local)    │                │  ECR — Docker images    │
│  Docker Compose    │                │  DynamoDB — metadata    │
│  Ollama (SLMs)     │                │  CloudWatch — monitoring│
└────────────────────┘                │  Secrets Manager        │
                                      └─────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- AWS CLI (configured, optional for local dev)
- Terraform >= 1.5 (for infrastructure)

### Local Development

```bash
# Start all services (API, frontend, MLflow, Ollama)
make dev

# Open the web UI
make web        # http://localhost:3000

# Open MLflow UI
make mlflow-ui  # http://localhost:5000

# Stop everything
make dev-down
```

### Manual Setup (without Docker)

```bash
# Backend
cd web/backend
pip install -e "../../.[api]"
uvicorn web.backend.main:app --reload --port 8000

# Frontend
cd web/frontend
npm install
npm run dev

# MLflow
mlflow server --host 0.0.0.0 --port 5000
```

## Project Structure

```
├── web/
│   ├── backend/           # FastAPI API server
│   │   ├── main.py        # App factory, CORS, lifespan
│   │   ├── routers/       # experiments, models, results, infrastructure, benchmarks
│   │   ├── services/      # experiment_service, aws_service, mlflow_service
│   │   ├── schemas.py     # Pydantic v2 models
│   │   └── dependencies.py
│   └── frontend/          # Next.js 14 App Router
│       ├── app/           # Pages: dashboard, experiments, results, infrastructure
│       ├── components/    # UI components + shadcn
│       ├── hooks/         # React Query + SSE hooks
│       └── lib/           # API client, utilities
├── mlops/
│   ├── tracking.py        # MLflowTracker class
│   ├── callbacks.py       # RunnerCallbacks for SSE integration
│   └── registry.py        # Model registration helpers
├── infrastructure/
│   └── terraform/
│       ├── modules/       # vpc, ec2, s3, ecr, dynamodb, iam, cloudwatch, secrets
│       └── environments/  # dev (t3.medium), prod (g4dn.xlarge + spot)
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.runner
│   ├── Dockerfile.mlflow
│   └── docker-compose.yml
├── .github/workflows/
│   ├── ci.yml             # Test + lint + terraform validate
│   ├── deploy.yml         # Build → ECR → Terraform apply
│   └── nightly.yml        # Scheduled benchmark runs
└── Makefile               # dev, tf-*, ecr-login, push-*
```

## Web UI

| Page | Description |
|------|-------------|
| **Dashboard** | Summary cards, EATS gauge, accuracy vs LLM call ratio scatter plot |
| **Experiments** | List all runs, launch new experiments with config form |
| **Live Progress** | SSE-powered real-time progress bar and metric updates |
| **Results** | Browse and compare up to 4 experiments side-by-side |
| **Infrastructure** | EC2 instance management, cost estimates |

## AWS Infrastructure

All infrastructure is managed via Terraform with remote state in S3 + DynamoDB locking.

```bash
make tf-init    # Initialize Terraform
make tf-plan    # Preview changes
make tf-apply   # Apply (with confirmation)
make tf-destroy # Destroy (with warning)
```

### Environments

| | Dev | Prod |
|---|---|---|
| EC2 | t3.medium | g4dn.xlarge (GPU, spot) |
| NAT Gateway | No | Yes |
| AZs | 1 | 2 |
| Spot | No | Yes |

## CI/CD Pipeline

- **Every push/PR**: Python tests + linting, frontend lint + typecheck, Terraform validate
- **Push to main**: Build Docker images → push to ECR → Terraform apply
- **Nightly (2am UTC)**: Run full benchmark suite, upload to S3, Slack notification

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/models` | List available SLMs/LLMs |
| POST | `/api/experiments` | Launch experiment |
| GET | `/api/experiments` | List all experiments |
| GET | `/api/experiments/{id}/stream` | SSE progress stream |
| GET | `/api/results/compare?ids=a,b,c` | Compare experiments |
| GET | `/api/infrastructure/instances` | List EC2 instances |
| GET | `/api/infrastructure/costs` | Cost estimates |

## Environment Variables

Create a `.env` file in the project root:

```env
THESIS_OPENAI_API_KEY=sk-...
THESIS_TOGETHER_API_KEY=...
THESIS_AWS_REGION=eu-west-1
THESIS_S3_RESULTS_BUCKET=thesis-results-dev
THESIS_MLFLOW_TRACKING_URI=http://localhost:5000
THESIS_OLLAMA_BASE_URL=http://localhost:11434
```

## Docker Images

```bash
make ecr-login    # Authenticate with ECR
make push-api     # Build and push API image
make push-runner  # Build and push runner image
```
