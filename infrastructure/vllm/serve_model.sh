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
    _serve "meta-llama/Llama-3.3-70B-Instruct" 8000 "--quantization awq --served-model-name meta-llama/Llama-3.3-70B-Instruct --gpu-memory-utilization 0.85"
    ;;
  multi_agent)
    _serve "Qwen/Qwen3.5-4B" 8001 "--served-model-name Qwen/Qwen3.5-4B --gpu-memory-utilization 0.12"
    _serve "google/gemma-4-E4B-it" 8002 "--served-model-name google/gemma-4-E4B-it --gpu-memory-utilization 0.10"
    _serve "meta-llama/Llama-3.2-3B-Instruct" 8003 "--served-model-name meta-llama/Llama-3.2-3B-Instruct --gpu-memory-utilization 0.10"
    ;;
  speculative)
    _serve "meta-llama/Llama-3.3-70B-Instruct" 8000 "--quantization awq --served-model-name meta-llama/Llama-3.3-70B-Instruct --gpu-memory-utilization 0.70"
    _serve "Qwen/Qwen3.5-4B" 8001 "--served-model-name Qwen/Qwen3.5-4B --gpu-memory-utilization 0.12"
    ;;
  all)
    _serve "meta-llama/Llama-3.3-70B-Instruct" 8000 "--quantization awq --served-model-name meta-llama/Llama-3.3-70B-Instruct --gpu-memory-utilization 0.70"
    _serve "Qwen/Qwen3.5-4B" 8001 "--served-model-name Qwen/Qwen3.5-4B --gpu-memory-utilization 0.12"
    _serve "google/gemma-4-E4B-it" 8002 "--served-model-name google/gemma-4-E4B-it --gpu-memory-utilization 0.10"
    _serve "meta-llama/Llama-3.2-3B-Instruct" 8003 "--served-model-name meta-llama/Llama-3.2-3B-Instruct --gpu-memory-utilization 0.10"
    ;;
  *)
    echo "Unknown setup: $SETUP" >&2
    exit 1
    ;;
esac

echo "All servers launched. Waiting..."
wait
