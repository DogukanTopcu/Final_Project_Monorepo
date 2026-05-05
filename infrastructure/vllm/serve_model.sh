#!/usr/bin/env bash
# Convenience launcher for vLLM models without Docker.
# Usage: ./serve_model.sh <setup_name>
#   setup_name: monolithic | multi_agent | speculative | all

set -euo pipefail

SETUP="${1:-monolithic}"
HF_TOKEN="${HF_TOKEN:-}"

_serve() {
  local model="$1" port="$2" extra="${3:-}"
  echo "Starting $model on port $port..."
  python -m vllm.entrypoints.openai.api_server \
    --model "$model" \
    --max-model-len 4096 \
    --port "$port" \
    ${extra} &
  echo "PID $! → $model"
}

case "$SETUP" in
  monolithic)
    _serve "meta-llama/Meta-Llama-3-70B-Instruct" 8000 "--quantization awq --gpu-memory-utilization 0.85"
    ;;
  multi_agent)
    _serve "meta-llama/Meta-Llama-3-8B-Instruct" 8001 "--gpu-memory-utilization 0.12"
    _serve "codellama/CodeLlama-7b-Instruct-hf"  8002 "--gpu-memory-utilization 0.10"
    _serve "mistralai/Mistral-7B-Instruct-v0.3"  8003 "--gpu-memory-utilization 0.10"
    ;;
  speculative)
    _serve "meta-llama/Meta-Llama-3-70B-Instruct" 8000 "--quantization awq --gpu-memory-utilization 0.70"
    _serve "meta-llama/Meta-Llama-3-8B-Instruct"  8001 "--gpu-memory-utilization 0.12"
    ;;
  all)
    _serve "meta-llama/Meta-Llama-3-70B-Instruct" 8000 "--quantization awq --gpu-memory-utilization 0.70"
    _serve "meta-llama/Meta-Llama-3-8B-Instruct"  8001 "--gpu-memory-utilization 0.12"
    _serve "codellama/CodeLlama-7b-Instruct-hf"   8002 "--gpu-memory-utilization 0.10"
    _serve "mistralai/Mistral-7B-Instruct-v0.3"   8003 "--gpu-memory-utilization 0.10"
    ;;
  *)
    echo "Unknown setup: $SETUP" >&2
    exit 1
    ;;
esac

echo "All servers launched. Waiting..."
wait
