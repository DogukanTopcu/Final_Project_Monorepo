from __future__ import annotations

import os
import time

import httpx
from fastapi import APIRouter, Depends

from core.model_catalog import LLM_MODEL_IDS, SLM_MODEL_IDS, get_model_spec
from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ModelInfo, ModelListResponse, ModelPingResponse

router = APIRouter(tags=["models"])

def _provider_label(provider: str) -> str:
    if provider == "openai_compatible":
        return "vllm"
    return provider


def _build_model_info(model_id: str) -> ModelInfo:
    spec = get_model_spec(model_id)
    if spec is None:
        raise ValueError(f"Unknown model: {model_id}")
    return ModelInfo(
        id=spec.id,
        name=spec.name,
        provider=_provider_label(spec.provider),
        type=spec.kind,
    )


SLM_MODELS = [_build_model_info(model_id) for model_id in SLM_MODEL_IDS]
LLM_MODELS = [_build_model_info(model_id) for model_id in LLM_MODEL_IDS]


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    return ModelListResponse(slm=SLM_MODELS, llm=LLM_MODELS)


@router.get("/models/{model_id}/ping", response_model=ModelPingResponse)
async def ping_model(model_id: str, settings: Settings = Depends(get_settings)):
    model = None
    for m in SLM_MODELS + LLM_MODELS:
        if m.id == model_id:
            model = m
            break

    if model is None:
        return ModelPingResponse(model_id=model_id, reachable=False)

    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if model.provider == "ollama":
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                reachable = resp.status_code == 200
            elif model.provider == "vllm":
                spec = get_model_spec(model.id)
                if spec is None:
                    reachable = False
                else:
                    base_url = os.getenv(spec.base_url_env or "", spec.base_url_default or "")
                    resp = await client.get(f"{base_url.rstrip('/')}/models")
                    reachable = resp.status_code == 200
            else:
                reachable = False
    except Exception:
        reachable = False

    latency_ms = (time.time() - start) * 1000
    return ModelPingResponse(
        model_id=model_id,
        reachable=reachable,
        latency_ms=round(latency_ms, 2) if reachable else None,
    )
