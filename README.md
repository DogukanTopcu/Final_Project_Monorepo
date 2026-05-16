# Thesis Experiment Platform — Monorepo

An end-to-end platform for running, tracking, and comparing SLM/LLM experiments across three architectures (Routing, Multi-Agent, Ensemble), automated benchmarks, UI-backed human preference evaluation, and full AWS/MLOps infrastructure.

## Architecture Overview

```
Local Machine                          AWS Cloud
┌────────────────────┐                ┌─────────────────────────┐
│  Next.js Frontend  │───────────────▶│  EC2 (CPU) — API/MLflow │
│  FastAPI Backend   │                │  EC2 (GPU) — model hosts│
│  ExperimentRunner  │                │  S3 — results/artifacts │
│  MLflow (local)    │                │  ECR — Docker images    │
│  Docker Compose    │                │  DynamoDB — metadata    │
│  Ollama + vLLM     │                │  CloudWatch — monitoring│
└────────────────────┘                │  Secrets Manager        │
                                      └─────────────────────────┘
```

## Selected Model Pool

The repo is normalized around the following canonical aliases:

| Tier | Repo alias | Runtime checkpoint |
|------|------------|--------------------|
| Heavy LLM | `kimi-k2.6-1t` | `moonshotai/Kimi-K2.6` |
| Heavy LLM | `qwen3.5-397b-a17b` | `Qwen/Qwen3.5-397B-A17B` |
| Heavy LLM | `gpt-oss-120b` | `openai/gpt-oss-120b` |
| Heavy LLM | `llama3.3-70b` | `meta-llama/Llama-3.3-70B-Instruct` |
| Light LLM | `qwen3.5-27b` | `qwen3.5:27b` |
| Light LLM | `gpt-oss-20b` | `openai/gpt-oss-20b` |
| Light LLM | `gemma4-31b` | `gemma4:31b` |
| MoE | `qwen3.5-122b-a10b` | `qwen3.5:122b` |
| MoE | `gemma4-26b-a4b` | `gemma4:26b` |
| MoE | `qwen3.5-35b-a3b` | `qwen3.5:35b` |
| SLM | `gemma4-4b` | `gemma4:e4b` |
| SLM | `qwen3.5-4b` | `qwen3.5:4b` |
| SLM | `llama3.2-3b` | `llama3.2:3b` |

Notes:
- User shorthand `Qwen 3.5 (396B)` is normalized to the official checkpoint `Qwen/Qwen3.5-397B-A17B`.
- User shorthand `Gemma 4 (4B)` is normalized to the effective-parameter checkpoint `gemma4:e4b` / `google/gemma-4-E4B-it`.
- Local development can keep using Ollama for the smaller aliases.
- Production/AWS can switch the same aliases to OpenAI-compatible vLLM endpoints by setting `THESIS_FORCE_VLLM=1`.

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
├── training/
│   ├── config.py          # LoRA/QLoRA training config schema
│   ├── datasets.py        # SFT JSONL preparation and split CLI
│   ├── train_lora.py      # Optional LoRA/QLoRA fine-tuning CLI
│   ├── registry.py        # Fine-tuned adapter registry
│   └── configs/           # Coding/domain pilot training configs
├── infrastructure/
│   └── terraform/
│       ├── modules/       # vpc, ec2, s3, ecr, dynamodb, iam, cloudwatch, secrets
│       └── environments/  # dev (t3.micro), prod (CPU API + optional model-specific GPU hosts)
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

## Benchmark Scope

| Benchmark | Purpose |
|-----------|---------|
| **MMLU / GSM8K / ARC / HellaSwag / TruthfulQA** | Automated accuracy benchmarks for reasoning, math, commonsense, and truthfulness |
| **HumanEval (project-specific)** | UI-backed human preference benchmark: prepared-prompt LLM Arena plus live user chat comparisons |
| **Custom Stratified Coding** | Easy/medium/hard coding problem set with versioned prompts, tests, and difficulty labels |

## Fine-Tuning Scope

Fine-tuning is kept as a separate ablation track under `training/`. The primary architecture experiments should keep base models fixed; fine-tuned SLMs are compared separately against base SLMs, orchestration variants, and LLM baselines.

```bash
pip install -e ".[training]"
python -m training.datasets prepare-sft --input training/data/raw/coding_pilot.jsonl --output-dir training/data/processed/coding_pilot
python -m training.train_lora --config training/configs/qlora_coding_pilot.yaml
```

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
| EC2 | `t3.micro` runner | `t3.large` API host + opt-in GPU model hosts |
| NAT Gateway | No | Yes |
| AZs | 1 | 2 |
| Spot | No | Disabled by default for serving hosts |

### Prod Model Hosts

Enable only the models you need in `infrastructure/terraform/environments/prod/terraform.tfvars` via `enabled_vllm_models`.

| Model alias | Default prod host |
|---|---|
| `qwen3.5-4b` | `g5.2xlarge` |
| `gemma4-4b` | `g5.2xlarge` |
| `llama3.2-3b` | `g5.2xlarge` |
| `gpt-oss-20b` | `g5.2xlarge` |
| `qwen3.5-27b` | `g6e.4xlarge` |
| `gemma4-31b` | `g6e.4xlarge` |
| `qwen3.5-35b-a3b` | `g6e.4xlarge` |
| `gemma4-26b-a4b` | `g6e.4xlarge` |
| `llama3.3-70b` | `g6e.12xlarge` |
| `gpt-oss-120b` | `p5.4xlarge` |
| `qwen3.5-122b-a10b` | `g6e.48xlarge` |
| `qwen3.5-397b-a17b` | `p5e.48xlarge` |
| `kimi-k2.6-1t` | `p5e.48xlarge` |

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
THESIS_AWS_REGION=eu-central-1
THESIS_S3_RESULTS_BUCKET=thesis-results-dev
THESIS_MLFLOW_TRACKING_URI=http://localhost:5000
THESIS_OLLAMA_BASE_URL=http://localhost:11434
THESIS_FORCE_VLLM=0
VLLM_LLAMA33_70B_URL=http://localhost:8000/v1
VLLM_QWEN35_4B_URL=http://localhost:8001/v1
VLLM_GEMMA4_E4B_URL=http://localhost:8002/v1
VLLM_LLAMA32_3B_URL=http://localhost:8003/v1
VLLM_QWEN35_27B_URL=http://localhost:8004/v1
VLLM_GPT_OSS_20B_URL=http://localhost:8005/v1
VLLM_GEMMA4_31B_URL=http://localhost:8006/v1
VLLM_QWEN35_35B_A3B_URL=http://localhost:8007/v1
VLLM_GEMMA4_26B_A4B_URL=http://localhost:8008/v1
VLLM_QWEN35_122B_A10B_URL=http://localhost:8009/v1
VLLM_KIMI_K26_1T_URL=http://localhost:8010/v1
VLLM_QWEN35_397B_A17B_URL=http://localhost:8011/v1
VLLM_GPT_OSS_120B_URL=http://localhost:8012/v1
```

## Docker Images

```bash
make ecr-login    # Authenticate with ECR
make push-api     # Build and push API image
make push-runner  # Build and push runner image
```
