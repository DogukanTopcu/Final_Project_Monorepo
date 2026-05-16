# WP1 Infrastructure Setup Runbook

This runbook operationalizes `PLAN.md` WP1 for local/GPU-server execution.

## 1. Prerequisites

- NVIDIA GPU driver installed (`nvidia-smi` must work).
- Docker + Docker Compose plugin installed.
- NVIDIA Container Toolkit installed (for `runtime: nvidia` services).
- Python 3.11 available.
- Hugging Face token with access to required model repos.

## 2. Environment Setup

Create `.env` from `.env.example` and fill at least:

- `HF_TOKEN`
- `MLFLOW_TRACKING_URI`
- `VLLM_LLAMA33_70B_URL`
- `VLLM_QWEN35_4B_URL`
- `VLLM_GEMMA4_E4B_URL`
- `VLLM_LLAMA32_3B_URL`
- `CODECARBON_PROJECT_NAME`

## 3. Python Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

If you run vLLM directly (without docker):

```bash
pip install "vllm==0.4.3"
```

## 4. Start Serving Stack

### Option A: Docker (recommended)

From repository root:

```bash
docker compose -f infrastructure/vllm/docker-compose.yml up -d llama33-70b
docker compose -f infrastructure/vllm/docker-compose.yml --profile multi-agent up -d qwen35-4b gemma4-e4b llama32-3b
```

### Option B: Native vLLM launcher

```bash
chmod +x infrastructure/vllm/serve_model.sh
./infrastructure/vllm/serve_model.sh all
```

## 5. Verification

### GPU check

```bash
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv
```

### vLLM health

```bash
curl -fsS http://localhost:8000/v1/models | jq .
curl -fsS http://localhost:8001/v1/models | jq .
curl -fsS http://localhost:8002/v1/models | jq .
curl -fsS http://localhost:8003/v1/models | jq .
```

### MLflow + tests

```bash
mlflow ui --port 5000
pytest tests/ -v
```

### Dry run experiment

```bash
python -m experiments.run_experiment --architecture all --benchmark mmlu --n_samples 1 --dry_run
```

## 6. WP1 Exit Criteria

- `nvidia-smi` reports target GPU as available.
- All required model endpoints return `/v1/models`.
- MLflow UI is reachable on `http://localhost:5000`.
- Core test suite executes successfully (`pytest tests/ -v`).
- Dry run passes config validation without runtime architecture failures.
