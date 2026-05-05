from __future__ import annotations

import time

import httpx
from fastapi import APIRouter, Depends

from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ModelInfo, ModelListResponse, ModelPingResponse

router = APIRouter(tags=["models"])

SLM_MODELS = [
    ModelInfo(id="phi3-mini", name="Phi-3 Mini", provider="ollama", type="slm"),
    ModelInfo(id="qwen2-1.5b", name="Qwen2 1.5B", provider="ollama", type="slm"),
    ModelInfo(id="llama3.2-3b", name="Llama 3.2 3B", provider="ollama", type="slm"),
]

LLM_MODELS = [
    ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", type="llm"),
    ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", type="llm"),
    ModelInfo(
        id="llama-3.1-70b",
        name="Llama 3.1 70B",
        provider="together",
        type="llm",
    ),
]


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
            elif model.provider == "openai":
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                )
                reachable = resp.status_code == 200
            elif model.provider == "together":
                resp = await client.get(
                    "https://api.together.xyz/v1/models",
                    headers={"Authorization": f"Bearer {settings.together_api_key}"},
                )
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
