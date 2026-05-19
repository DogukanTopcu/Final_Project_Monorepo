from __future__ import annotations

import time

import httpx
from fastapi import APIRouter, Depends

from core.model_catalog import SELECTED_MODELS
from core.models import get_model_runtime_status
from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ModelInfo, ModelListResponse, ModelPingResponse

router = APIRouter(tags=["models"])


@router.get("/models", response_model=ModelListResponse)
async def list_models(settings: Settings = Depends(get_settings)):
    warnings: list[str] = []
    slm_models: list[ModelInfo] = []
    llm_models: list[ModelInfo] = []

    for spec in SELECTED_MODELS:
        status = get_model_runtime_status(spec.id)
        model = ModelInfo(
            id=spec.id,
            name=spec.name,
            family=spec.family,
            tier=spec.tier,
            provider=spec.provider,
            runtime_provider=str(status.get("provider", spec.provider)),
            type=spec.kind,
            configured=bool(status.get("available", False)),
            status="ready" if bool(status.get("available", False)) else "unavailable",
            base_url=str(status.get("base_url", "")) or None,
            reason=str(status.get("reason", "")) or None,
        )
        if spec.kind == "slm":
            slm_models.append(model)
        else:
            llm_models.append(model)

    if not any(model.configured for model in slm_models):
        warnings.append("No runnable SLM is configured. Set a VLLM_* endpoint or start Ollama.")
    if not any(model.configured for model in llm_models):
        warnings.append("No runnable LLM is configured. Set a VLLM_* endpoint or matching API key.")

    return ModelListResponse(
        slm=slm_models,
        llm=llm_models,
        runtime_mode="forced_vllm" if settings.force_vllm else "mixed",
        force_vllm=settings.force_vllm,
        warnings=warnings,
    )


@router.get("/models/{model_id}/ping", response_model=ModelPingResponse)
async def ping_model(model_id: str, settings: Settings = Depends(get_settings)):
    del settings
    start = time.time()
    status = get_model_runtime_status(model_id)
    if not bool(status.get("available")):
        return ModelPingResponse(model_id=model_id, reachable=False, latency_ms=None)

    provider = str(status.get("provider", "unknown"))
    base_url = str(status.get("base_url", "")).rstrip("/")
    if not base_url:
        return ModelPingResponse(model_id=model_id, reachable=False, latency_ms=None)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if provider == "ollama":
                response = await client.get(f"{base_url}/api/tags")
            else:
                response = await client.get(f"{base_url}/models")
            reachable = response.status_code == 200
    except Exception:
        reachable = False

    return ModelPingResponse(
        model_id=model_id,
        reachable=reachable,
        latency_ms=round((time.time() - start) * 1000, 2) if reachable else None,
    )
