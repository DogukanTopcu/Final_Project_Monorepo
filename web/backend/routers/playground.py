"""Single-model playground endpoint.

Sends a one-shot prompt to a single configured model and returns the response
along with measurement data (latency, tokens, cost). Respects shared-host
lock semantics: if the target alias is on a shared host that is currently
serving a different alias, we return a clear 409 instead of letting vLLM
respond with a vague 404.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.hosts import get_host_for_model, resolve_base_url
from core.model_catalog import get_expected_runtime_model_ids
from core.models import get_model, get_model_runtime_status
from core.token_budget import compute_completion_budget
from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import PlaygroundChatRequest, PlaygroundChatResponse
from web.backend.services.model_host_service import (
    fetch_served_model_ids,
    reserve_llm_host,
)


router = APIRouter(prefix="/playground", tags=["playground"])


def _ensure_alias_active_on_host(model_id: str) -> None:
    """Raise 409 if the alias lives on a shared host that currently serves a
    different model — so the user sees a clear message instead of a vLLM 404.
    """
    host = get_host_for_model(model_id)
    if host is None or not host.shared:
        return

    base_url = resolve_base_url(model_id)
    if not base_url:
        return

    expected = get_expected_runtime_model_ids(model_id)
    if not expected:
        return

    served = fetch_served_model_ids(base_url.rstrip("/"))
    if not served:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{host.label} is not reachable at {base_url}. "
                f"Check that the vLLM container is running and port 8000 is open."
            ),
        )
    if not (served & expected):
        served_list = ", ".join(sorted(served)) or "<none>"
        raise HTTPException(
            status_code=409,
            detail=(
                f"{host.label} currently serves {served_list}, not {model_id}. "
                f"Switch the container on the shared host before calling this model."
            ),
        )


@router.post("/chat", response_model=PlaygroundChatResponse)
def playground_chat(
    req: PlaygroundChatRequest,
    settings: Settings = Depends(get_settings),
) -> PlaygroundChatResponse:
    runtime = get_model_runtime_status(req.model_id)
    if not bool(runtime.get("available")):
        raise HTTPException(
            status_code=400,
            detail=str(runtime.get("reason", f"{req.model_id} is unavailable.")),
        )

    # Respect shared-host locking: this may trigger an autoswitch when enabled,
    # otherwise it falls back to nullcontext.
    reservation = reserve_llm_host(req.model_id, settings)

    try:
        provider = get_model(req.model_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with reservation:
        # Final pre-flight check after any switch attempt.
        _ensure_alias_active_on_host(req.model_id)

        prompt = req.prompt if not req.system else f"{req.system}\n\n{req.prompt}"
        budget = compute_completion_budget(
            provider,
            prompt,
            task_type="open",
            role="playground",
            requested_max_tokens=req.max_tokens,
        )
        t0 = time.perf_counter()
        try:
            text, _conf, in_tokens, out_tokens, cost = provider.generate(
                prompt,
                temperature=req.temperature,
                max_tokens=budget,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        total_latency_ms = (time.perf_counter() - t0) * 1000.0
        metadata = dict(getattr(provider, "last_generation_metadata", {}) or {})
        model_latency_ms = metadata.get("latency_ms_server")
        model_latency_ms = float(model_latency_ms) if model_latency_ms is not None else None

    return PlaygroundChatResponse(
        model_id=req.model_id,
        text=text,
        latency_ms=round(total_latency_ms, 2),
        model_latency_ms=round(model_latency_ms, 2) if model_latency_ms is not None else None,
        completed_at=datetime.fromisoformat(str(metadata.get("completed_at"))) if metadata.get("completed_at") else datetime.now(timezone.utc),
        input_tokens=in_tokens,
        output_tokens=out_tokens,
        effective_max_tokens=int(metadata.get("effective_max_tokens") or budget),
        cost_usd=cost,
        energy_kwh=float(metadata.get("energy_kwh") or 0.0),
        co2_g=float(metadata.get("co2_g") or 0.0),
        gpu_power_w=float(metadata.get("gpu_power_w") or 0.0),
        infra_cost_usd=float(metadata.get("infra_cost_usd") or 0.0),
        base_url=resolve_base_url(req.model_id),
        finish_reason=str(metadata.get("finish_reason") or "unknown"),
    )
