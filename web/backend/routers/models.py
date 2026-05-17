from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import APIRouter, Depends

from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ModelInfo, ModelListResponse, ModelPingResponse

router = APIRouter(tags=["models"])

LLM_MODELS = [
    ModelInfo(id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", type="llm"),
    ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", type="llm"),
    ModelInfo(
        id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
        provider="google",
        type="llm",
    ),
    ModelInfo(
        id="gemini-2.5-flash-lite",
        name="Gemini 2.5 Flash-Lite",
        provider="google",
        type="llm",
    ),
    ModelInfo(
        id="llama-3.1-70b",
        name="Llama 3.1 70B",
        provider="together",
        type="llm",
    ),
]


async def fetch_ollama_tags(base_url: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{base_url.rstrip('/')}/api/tags")
        response.raise_for_status()
    return response.json().get("models", [])


async def discover_ollama_models(
    settings: Settings,
) -> tuple[list[ModelInfo], bool, list[str]]:
    try:
        models = await fetch_ollama_tags(settings.ollama_base_url)
    except Exception:
        return [], False, [
            f"Ollama is unreachable at {settings.ollama_base_url}. Start `ollama serve` to use local SLMs."
        ]

    slm_models = [
        ModelInfo(
            id=model["name"],
            name=model["name"],
            provider="ollama",
            type="slm",
            status="installed",
        )
        for model in models
        if model.get("name")
    ]

    warnings: list[str] = []
    if not slm_models:
        warnings.append("Ollama is reachable, but no local models are installed yet.")
    return slm_models, True, warnings


@router.get("/models", response_model=ModelListResponse)
async def list_models(settings: Settings = Depends(get_settings)):
    slm_models, ollama_reachable, warnings = await discover_ollama_models(settings)
    llm_models = [
        model.model_copy(
            update={
                "status": (
                    "configured"
                    if settings.openai_api_key
                    else "missing_api_key"
                )
                if model.provider == "openai"
                else (
                    "configured"
                    if settings.gemini_api_key
                    else "missing_api_key"
                )
                if model.provider == "google"
                else "available"
            }
        )
        for model in LLM_MODELS
    ]
    return ModelListResponse(
        slm=slm_models,
        llm=llm_models,
        ollama_reachable=ollama_reachable,
        openai_configured=bool(settings.openai_api_key),
        gemini_configured=bool(settings.gemini_api_key),
        warnings=warnings,
    )


@router.get("/models/{model_id}/ping", response_model=ModelPingResponse)
async def ping_model(model_id: str, settings: Settings = Depends(get_settings)):
    start = time.time()
    try:
        slm_models, _, _ = await discover_ollama_models(settings)
        slm_ids = {model.id for model in slm_models}
        openai_ids = {model.id for model in LLM_MODELS if model.provider == "openai"}
        gemini_ids = {model.id for model in LLM_MODELS if model.provider == "google"}
        together_ids = {model.id for model in LLM_MODELS if model.provider == "together"}

        async with httpx.AsyncClient(timeout=5.0) as client:
            if model_id in slm_ids:
                response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
                reachable = response.status_code == 200
            elif model_id in openai_ids:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                )
                reachable = response.status_code == 200
            elif model_id in gemini_ids:
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    params={"key": settings.gemini_api_key},
                )
                reachable = response.status_code == 200
            elif model_id in together_ids:
                response = await client.get(
                    "https://api.together.xyz/v1/models",
                    headers={"Authorization": f"Bearer {settings.together_api_key}"},
                )
                reachable = response.status_code == 200
            else:
                reachable = False
    except Exception:
        reachable = False

    return ModelPingResponse(
        model_id=model_id,
        reachable=reachable,
        latency_ms=round((time.time() - start) * 1000, 2) if reachable else None,
    )
