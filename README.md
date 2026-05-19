# Thesis Experiment Platform

Monorepo for running thesis experiments that compare multiple SLM/LLM orchestration architectures over a shared benchmark and measurement stack.

The codebase is built around:
- a local control plane: FastAPI backend, Next.js frontend, MLflow
- remote OpenAI-compatible inference endpoints: vLLM hosts on GCP and optional heavy hosts elsewhere
- a shared experiment contract: every architecture receives the same `Query` and returns the same `Response`

## Repo Truths

- `HumanEval` in this repository is a project-specific human preference evaluation workflow, not the OpenAI code-generation dataset.
- `custom_stratified` is intended to be the easy/medium/hard coding benchmark track.
- `eats` is a metric, not a benchmark.
- Supported experiment architectures in the active product surface are:
  - `routing`
  - `multi_agent`
  - `ensemble`

## Current Runtime Topology

The working deployment model from the current experiments is:

| Layer | Runtime | Purpose |
|---|---|---|
| Control plane | Local machine | FastAPI backend, Next.js frontend, MLflow, experiment runner |
| SLM tier | GCP L4 hosts | `gemma4-4b`, `qwen3.5-4b`, `llama3.2-3b` |
| Mid-tier LLM tier | GCP G4 / RTX PRO 6000 shared host | `gpt-oss-20b`, `qwen3.5-27b`, `gemma4-31b`, `qwen3.5-35b-a3b`, `gemma4-26b-a4b`, `qwen3.5-122b-a10b` |
| Heavy tier | Optional Nebius H100/H200 class host | `llama3.3-70b`, `gpt-oss-120b`, `qwen3.5-397b-a17b`, `kimi-k2.6-1t` |

Important operational detail:
- the RTX6000 host is treated as a shared mid-tier server
- the heavy host is also treated as a shared server
- only one large model should be active on a shared host at a time

## Canonical Model Aliases

These aliases are the source of truth used by the backend, CLI runner, and frontend.

| Tier | Alias |
|---|---|
| SLM | `gemma4-4b`, `qwen3.5-4b`, `llama3.2-3b` |
| Light LLM | `gpt-oss-20b`, `qwen3.5-27b`, `gemma4-31b` |
| MoE / mid-tier | `qwen3.5-35b-a3b`, `gemma4-26b-a4b`, `qwen3.5-122b-a10b` |
| Heavy LLM | `llama3.3-70b`, `gpt-oss-120b`, `qwen3.5-397b-a17b`, `kimi-k2.6-1t` |

## Supported Architectures

| Architecture | Repo id | Summary |
|---|---|---|
| Architecture A | `routing` | SLM drafts first, low-confidence cases escalate to the selected LLM |
| Architecture B | `multi_agent` | Proponent-opponent-arbitrator flow over the same query |
| Architecture C | `ensemble` | Multiple SLM passes vote; optional LLM tiebreak can be enabled |

## Supported Benchmarks

Launchable automated benchmarks:
- `mmlu`
- `arc`
- `hellaswag`
- `gsm8k`
- `truthfulqa`
- `custom_stratified`

Special case:
- `humaneval` is reserved for the UI-backed human preference workflow and is intentionally not part of the normal automated benchmark launcher.

## Measurement Model

Each `Response` now carries both output quality and resource data:
- `latency_ms`
- `input_tokens`
- `output_tokens`
- `llm_calls`
- `api_cost_usd`
- `infra_cost_usd`
- `cost_usd`
- `energy_kwh`
- `co2_g`
- `gpu_power_w`

Current energy and infra reporting policy:
- direct API costs are taken from provider-specific token pricing when applicable
- self-hosted remote runs estimate infra cost and energy from host profiles
- host-profile estimation is attached through `metadata["inference_steps"]`
- experiment-level summaries aggregate these values and log them to MLflow and JSON/Markdown reports

## Quick Start

### 1. Install Python dependencies

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill at least:
- `HF_TOKEN`
- `THESIS_FORCE_VLLM`
- `MLFLOW_TRACKING_URI`
- `THESIS_MLFLOW_TRACKING_URI`
- the `VLLM_*_URL` entries for the models you actually deployed

### 3. Start MLflow

```bash
mlflow server --host 127.0.0.1 --port 5000
```

### 4. Start the backend

```bash
source .venv/bin/activate
uvicorn web.backend.main:app --reload --host 127.0.0.1 --port 8000
```

The backend loads the repo-root `.env` automatically.

### 5. Start the frontend

```bash
cd web/frontend
npm install
npm run dev
```

Frontend:
- `http://localhost:3000`

Backend OpenAPI:
- `http://127.0.0.1:8000/docs`

MLflow:
- `http://127.0.0.1:5000`

## Validate Remote Model Endpoints

First check the backend model catalog view:

```bash
curl -fsS http://127.0.0.1:8000/models | jq .
```

Then check an endpoint directly:

```bash
curl -fsS http://<HOST_IP>:8000/v1/models | jq .
```

Expected behavior:
- the backend returns runnable SLM and LLM aliases
- the frontend launch form uses the same runtime status

## Run Experiments

### Web UI

Open:
- `http://localhost:3000/experiments/new`

Choose:
- one architecture
- one benchmark
- one SLM alias
- one LLM alias

### CLI

Example:

```bash
python -m experiments.run_experiment \
  --architecture routing \
  --benchmark mmlu \
  --n_samples 100 \
  --slm qwen3.5-4b \
  --llm gpt-oss-20b \
  --confidence_threshold 0.95 \
  --mlflow_uri http://127.0.0.1:5000
```

Results are written to:
- `results/exp_<id>.json`
- `results/exp_<id>.md`

## Working Deployment Notes

### GCP L4 hosts

Known working pattern:
- one model per host
- use vLLM OpenAI-compatible serving
- expose `:8000/v1`

### GCP G4 / RTX6000 shared host

Known working image family:
- `common-cu129-ubuntu-2404-nvidia-580`

Known working behavior:
- use a single shared container name
- switch the active mid-tier model when needed
- keep `.env` mapped to the current public IP

### Nebius heavy host

Heavy-tier provisioning remains optional.

Known constraint from current work:
- H200 spot capacity may fail with `NotEnoughResources`
- if that happens, retry later or fall back to H100

## Key Files

| Path | Purpose |
|---|---|
| `core/model_catalog.py` | Canonical aliases and endpoint env names |
| `core/models.py` | Provider adapters and runtime selection |
| `architectures/` | Architecture implementations |
| `benchmarks/` | Automated benchmark loaders |
| `experiments/runner.py` | Main execution loop |
| `evaluation/metrics.py` | Accuracy, latency, EATS, energy summary metrics |
| `evaluation/energy.py` | Host-profile resource estimation |
| `mlops/tracking.py` | MLflow logging |
| `web/backend/` | FastAPI control plane |
| `web/frontend/` | Next.js dashboard and launcher |
| `infrastructure/WP1_RUNBOOK.md` | Infra bring-up checklist and host notes |

## Additional Notes

- The frontend and backend are now aligned to the shared model catalog instead of hardcoded provider assumptions.
- The system no longer assumes Ollama-first or hosted-API-first operation.
- Remote vLLM endpoints are the primary experiment runtime path.
- Legacy files for monolithic or speculative variants may remain in the repo for reference, but the active experiment surface is `routing`, `multi_agent`, and `ensemble`.
