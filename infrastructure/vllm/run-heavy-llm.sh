#!/usr/bin/env bash
# Heavy host model switcher (H100/H200).
# Usage: ~/run-heavy-llm.sh <model>
#   model: llama3.3-70b | gpt-oss-120b
#
# Mirrors the run-mid-llm.sh pattern on the RTX6000 host.
# Only one model runs at a time on port 8000.

set -euo pipefail

CONTAINER_NAME="heavy-llm"
MODEL="${1:-}"
HF_TOKEN="${HF_TOKEN:-}"

if [[ -z "$MODEL" ]]; then
  echo "Usage: $0 <llama3.3-70b|gpt-oss-120b>" >&2
  exit 1
fi

if [[ -z "$HF_TOKEN" ]]; then
  echo "HF_TOKEN is not set. Export it first: export HF_TOKEN=hf_..." >&2
  exit 1
fi

case "$MODEL" in
  llama3.3-70b)
    HF_MODEL="meta-llama/Llama-3.3-70B-Instruct"
    # BF16 weights = 131 GiB on H200 (141 GB). 0.98 → 138 GB total, ~6 GB left for KV cache.
    # 8192 max_model_len keeps KV cache small enough to fit.
    EXTRA_ARGS="--max-model-len 8192 --gpu-memory-utilization 0.98"
    ;;
  gpt-oss-120b)
    HF_MODEL="openai/gpt-oss-120b"
    # Model ships as mxfp4 (NVIDIA Microscaling FP4) ≈ 60 GB weights.
    # Do NOT pass --quantization; vLLM reads it from model config automatically.
    # With ~60 GB model on 141 GB H200, plenty of room for KV cache.
    EXTRA_ARGS="--max-model-len 32768 --gpu-memory-utilization 0.90"
    ;;
  *)
    echo "Unknown model: $MODEL" >&2
    echo "Valid: llama3.3-70b, gpt-oss-120b" >&2
    exit 1
    ;;
esac

echo "Stopping $CONTAINER_NAME (if running)..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm   "$CONTAINER_NAME" 2>/dev/null || true

echo "Starting $MODEL ($HF_MODEL)..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  --gpus all \
  -p 8001:8000 \
  -e HUGGING_FACE_HUB_TOKEN="$HF_TOKEN" \
  -v /opt/hf-cache:/root/.cache/huggingface \
  vllm/vllm-openai:v0.19.1 \
  --model "$HF_MODEL" \
  --served-model-name "$HF_MODEL" \
  --port 8000 \
  $EXTRA_ARGS

echo ""
echo "Container started. Follow logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "Verify when ready:"
echo "  curl -fsS http://localhost:8000/v1/models | jq ."
