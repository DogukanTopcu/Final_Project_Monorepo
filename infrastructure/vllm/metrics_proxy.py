"""Thin FastAPI proxy in front of a local vLLM server.

Purpose:
- measure host-side inference latency (proxy -> vLLM -> proxy)
- attach CodeCarbon/NVML-derived energy data to the JSON response
- preserve the OpenAI-compatible API shape while appending a `_thesis` block

Run on each VM with:
  python infrastructure/vllm/metrics_proxy.py --listen-port 8000 --upstream http://127.0.0.1:8001/v1

Then run vLLM itself on port 8001.
"""
from __future__ import annotations

import argparse
import os
import time
from datetime import UTC, datetime
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from evaluation.energy import EnergyTracker, estimate_step_usage


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_none(item) for item in value]
    return value


def create_app(upstream_base_url: str) -> FastAPI:
    app = FastAPI(title="thesis-vllm-metrics-proxy", version="0.1.0")
    upstream = upstream_base_url.rstrip("/")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "upstream": upstream}

    @app.get("/v1/models")
    async def models() -> Response:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(f"{upstream}/models")
            return Response(content=r.content, status_code=r.status_code, media_type=r.headers.get("content-type"))
        except httpx.RequestError as exc:
            return JSONResponse({"error": f"Upstream vLLM is unreachable: {exc}"}, status_code=502)

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> Response:
        payload = await request.json()
        tracker = EnergyTracker(project_name="thesis_vllm_proxy")
        tracker.start()
        tracker.sample_gpu_power()
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                upstream_response = await client.post(f"{upstream}/chat/completions", json=payload)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            tracker.sample_gpu_power()
        except httpx.RequestError as exc:
            tracker.stop(total_tokens=0)
            return JSONResponse({"error": f"Upstream vLLM is unreachable: {exc}"}, status_code=502)

        if upstream_response.status_code >= 400:
            return Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                media_type=upstream_response.headers.get("content-type"),
            )

        data: dict[str, Any] = _drop_none(upstream_response.json())
        usage = data.get("usage", {}) if isinstance(data.get("usage"), dict) else {}
        completion_tokens = int(usage.get("completion_tokens", 0) or 0)
        prompt_tokens = int(usage.get("prompt_tokens", 0) or 0)
        total_tokens = prompt_tokens + completion_tokens
        reading = tracker.stop(total_tokens=total_tokens)

        model_id = str(payload.get("model", "") or "")
        infra = estimate_step_usage(model_id, latency_ms)
        finish_reason = "unknown"
        choices = data.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            finish_reason = str(choices[0].get("finish_reason") or "unknown")

        data["_thesis"] = {
            "latency_ms": round(latency_ms, 2),
            "completed_at": datetime.now(UTC).isoformat(),
            "effective_max_tokens": int(payload.get("max_tokens", 0) or 0),
            "finish_reason": finish_reason,
            "energy_kwh": float(reading.energy_kwh or infra.get("energy_kwh", 0.0)),
            "co2_g": float(reading.co2_g or infra.get("co2_g", 0.0)),
            "gpu_power_w": float(reading.gpu_power_w or infra.get("gpu_power_w", 0.0)),
            "infra_cost_usd": float(infra.get("infra_cost_usd", 0.0)),
        }

        headers = {
            "x-thesis-latency-ms": str(data["_thesis"]["latency_ms"]),
            "x-thesis-energy-kwh": str(data["_thesis"]["energy_kwh"]),
            "x-thesis-co2-g": str(data["_thesis"]["co2_g"]),
            "x-thesis-gpu-power-w": str(data["_thesis"]["gpu_power_w"]),
            "x-thesis-infra-cost-usd": str(data["_thesis"]["infra_cost_usd"]),
        }
        return JSONResponse(content=data, status_code=upstream_response.status_code, headers=headers)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-host", default="0.0.0.0")
    parser.add_argument("--listen-port", type=int, default=int(os.getenv("THESIS_PROXY_PORT", "8000")))
    parser.add_argument("--upstream", default=os.getenv("THESIS_VLLM_UPSTREAM", "http://127.0.0.1:8001/v1"))
    args = parser.parse_args()
    uvicorn.run(create_app(args.upstream), host=args.listen_host, port=args.listen_port)


if __name__ == "__main__":
    main()
