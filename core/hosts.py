"""Host topology catalog.

Maps model aliases to physical hosts, identifies which hosts are *shared*
(only one large model active at a time) and surfaces a stable host id for
the frontend lock indicators.

The classification mirrors README's "Current Runtime Topology" section.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable

from core.model_catalog import SELECTED_MODELS, ModelSpec, get_model_spec


@dataclass(frozen=True)
class HostSpec:
    host_id: str
    label: str
    shared: bool
    description: str = ""
    model_ids: tuple[str, ...] = field(default_factory=tuple)


# Static host catalog. Each host owns a fixed set of aliases; the live IP is
# resolved from the alias' VLLM_*_URL env var at runtime.
HOSTS: tuple[HostSpec, ...] = (
    HostSpec(
        host_id="l4-qwen-4b",
        label="GCP L4 — qwen3.5-4b",
        shared=False,
        description="Dedicated L4 host serving qwen3.5-4b only.",
        model_ids=("qwen3.5-4b",),
    ),
    HostSpec(
        host_id="l4-gemma-e4b",
        label="GCP L4 — gemma4-4b",
        shared=False,
        description="Dedicated L4 host serving gemma4-4b only.",
        model_ids=("gemma4-4b",),
    ),
    HostSpec(
        host_id="l4-llama-3b",
        label="GCP L4 — llama3.2-3b",
        shared=False,
        description="Dedicated L4 host serving llama3.2-3b only.",
        model_ids=("llama3.2-3b",),
    ),
    HostSpec(
        host_id="l4-ministral-3b",
        label="GCP L4 — ministral3-3b",
        shared=False,
        description="Dedicated L4 host serving ministral3-3b only.",
        model_ids=("ministral3-3b",),
    ),
    HostSpec(
        host_id="l4-phi4-mini",
        label="GCP L4 — phi4-mini",
        shared=False,
        description="Dedicated L4 host serving phi4-mini only.",
        model_ids=("phi4-mini",),
    ),
    HostSpec(
        host_id="rtx6000",
        label="GCP RTX6000 — shared mid-tier",
        shared=True,
        description=(
            "Shared host. Only one mid-tier LLM is active at a time; switching "
            "requires the autoswitch script or a manual restart."
        ),
        model_ids=(
            "gpt-oss-20b",
            "qwen3.5-27b",
            "gemma4-31b",
            "qwen3.5-35b-a3b",
            "gemma4-26b-a4b",
        ),
    ),
    HostSpec(
        host_id="heavy",
        label="Heavy host (H100/H200)",
        shared=True,
        description=(
            "Optional heavy-tier shared host. Capacity is limited; serve a "
            "single large model at a time."
        ),
        model_ids=(
            "llama3.3-70b",
            "gpt-oss-120b",
        ),
    ),
)


_MODEL_TO_HOST: dict[str, HostSpec] = {
    model_id: host for host in HOSTS for model_id in host.model_ids
}


def get_host_for_model(model_id: str) -> HostSpec | None:
    return _MODEL_TO_HOST.get(model_id)


def list_hosts() -> tuple[HostSpec, ...]:
    return HOSTS


def shared_host_ids() -> set[str]:
    return {host.host_id for host in HOSTS if host.shared}


def resolve_base_url(model_id: str) -> str | None:
    spec: ModelSpec | None = get_model_spec(model_id)
    if spec is None or spec.base_url_env is None:
        return None
    return os.environ.get(spec.base_url_env, spec.base_url_default)


def base_url_for_host(host: HostSpec) -> str | None:
    """Pick the first configured base URL among the host's models."""
    for model_id in host.model_ids:
        url = resolve_base_url(model_id)
        if url:
            return url.rstrip("/")
    return None


def host_models(host_id: str) -> Iterable[ModelSpec]:
    host = next((h for h in HOSTS if h.host_id == host_id), None)
    if host is None:
        return ()
    out: list[ModelSpec] = []
    for mid in host.model_ids:
        spec = get_model_spec(mid)
        if spec is not None:
            out.append(spec)
    return tuple(out)


def all_model_specs() -> Iterable[ModelSpec]:
    return SELECTED_MODELS
