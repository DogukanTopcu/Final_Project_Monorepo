# WP1 Infrastructure Setup Runbook

This runbook is the practical bring-up guide for the current experiment stack.

It assumes:
- local control plane on your machine
- remote vLLM hosts for model serving
- canonical aliases defined in `core/model_catalog.py`

## 1. Preflight

Required locally:
- Python 3.11
- Node.js 20+
- Docker
- MLflow
- `jq`
- Hugging Face token with access to any gated repos you plan to serve

Required on GPU hosts:
- working `nvidia-smi`
- Docker
- NVIDIA Container Toolkit
- public endpoint exposed on `:8000`

## 2. Local Control Plane

### Python environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### Frontend dependencies

```bash
cd web/frontend
npm install
cd ../..
```

### MLflow

```bash
mlflow server --host 127.0.0.1 --port 5000
```

### Backend

```bash
source .venv/bin/activate
uvicorn web.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd web/frontend
npm run dev
```

## 3. Environment File

Create `.env` from `.env.example` and fill:
- `HF_TOKEN`
- `THESIS_FORCE_VLLM`
- `MLFLOW_TRACKING_URI`
- `THESIS_MLFLOW_TRACKING_URI`
- the `VLLM_*_URL` values for deployed hosts

Current recommended default:

```env
THESIS_FORCE_VLLM=1
MLFLOW_TRACKING_URI=http://127.0.0.1:5000
THESIS_MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

## 4. GCP L4 SLM Hosts

Recommended layout:
- one host per SLM
- one vLLM server per host

Models:
- `gemma4-4b`
- `qwen3.5-4b`
- `llama3.2-3b`

Host checklist:

```bash
nvidia-smi
sudo docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

Serve a model:

```bash
sudo docker run -d \
  --name slm-serve \
  --restart unless-stopped \
  --gpus all \
  -p 8000:8000 \
  -e HUGGING_FACE_HUB_TOKEN="$HF_TOKEN" \
  -v /opt/hf-cache:/root/.cache/huggingface \
  vllm/vllm-openai:v0.19.1 \
  --model Qwen/Qwen3.5-4B \
  --served-model-name Qwen/Qwen3.5-4B \
  --port 8000 \
  --max-model-len 8192
```

Verification:

```bash
curl -fsS http://localhost:8000/v1/models | jq .
```

## 5. GCP G4 / RTX6000 Shared Mid-Tier Host

Known working image family:
- `common-cu129-ubuntu-2404-nvidia-580`

Known working verification:

```bash
nvidia-smi
```

This host should run exactly one mid-tier model at a time.

Suggested shared script pattern:

```bash
~/run-mid-llm.sh gpt-oss-20b
~/run-mid-llm.sh qwen3.5-27b
~/run-mid-llm.sh gemma4-31b
~/run-mid-llm.sh qwen3.5-35b-a3b
~/run-mid-llm.sh gemma4-26b-a4b
~/run-mid-llm.sh qwen3.5-122b-a10b
```

Verification:

```bash
sudo docker logs -f mid-llm
curl -fsS http://localhost:8000/v1/models | jq .
```

## 6. Optional Nebius Heavy Host

Use only if heavy-tier experiments are needed.

Recommended target:
- H200 spot if capacity exists
- H100 spot fallback otherwise

Known operational caveats:
- H200 spot can fail with `NotEnoughResources`
- if the instance is created through Nebius CLI, make sure SSH user data is injected at creation time

Minimal first checks after SSH:

```bash
whoami
nvidia-smi
```

Then:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl docker.io jq
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

And NVIDIA container runtime:

```bash
distribution=$(. /etc/os-release; echo ${ID}${VERSION_ID})

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -fsSL https://nvidia.github.io/libnvidia-container/${distribution}/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list >/dev/null

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verification:

```bash
sudo docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## 7. Register Endpoints in `.env`

Map each deployed endpoint to the alias env vars.

Example:

```env
THESIS_FORCE_VLLM=1

VLLM_QWEN35_4B_URL=http://<L4_QWEN_IP>:8000/v1
VLLM_GEMMA4_E4B_URL=http://<L4_GEMMA_IP>:8000/v1
VLLM_LLAMA32_3B_URL=http://<L4_LLAMA_IP>:8000/v1

VLLM_GPT_OSS_20B_URL=http://<RTX_IP>:8000/v1
VLLM_QWEN35_27B_URL=http://<RTX_IP>:8000/v1
VLLM_GEMMA4_31B_URL=http://<RTX_IP>:8000/v1
VLLM_QWEN35_35B_A3B_URL=http://<RTX_IP>:8000/v1
VLLM_GEMMA4_26B_A4B_URL=http://<RTX_IP>:8000/v1
VLLM_QWEN35_122B_A10B_URL=http://<RTX_IP>:8000/v1

VLLM_LLAMA33_70B_URL=http://<HEAVY_IP>:8000/v1
VLLM_GPT_OSS_120B_URL=http://<HEAVY_IP>:8000/v1
VLLM_QWEN35_397B_A17B_URL=http://<HEAVY_IP>:8000/v1
VLLM_KIMI_K26_1T_URL=http://<HEAVY_IP>:8000/v1
```

Restart the backend after changing `.env`.

## 8. Verify the Control Plane

Backend model discovery:

```bash
curl -fsS http://127.0.0.1:8000/models | jq .
```

Expected:
- runnable SLMs appear under `slm`
- runnable LLMs appear under `llm`
- `runtime_mode` reflects `THESIS_FORCE_VLLM`

## 9. Smoke Tests

### CLI smoke test

```bash
python -m experiments.run_experiment \
  --architecture routing \
  --benchmark mmlu \
  --n_samples 5 \
  --slm qwen3.5-4b \
  --llm gpt-oss-20b \
  --confidence_threshold 0.95 \
  --mlflow_uri http://127.0.0.1:5000
```

### Web smoke test

1. Open `http://localhost:3000/experiments/new`
2. Select a runnable SLM
3. Select a runnable LLM
4. Launch a 5-sample run

## 10. WP1 Exit Criteria

WP1 is complete when:
- backend, frontend, and MLflow all run locally
- `/models` reports the correct runtime availability
- at least one SLM host and one LLM host respond to `/v1/models`
- one CLI experiment succeeds
- one web-launched experiment succeeds
- JSON, Markdown, and MLflow outputs are produced for the same run
