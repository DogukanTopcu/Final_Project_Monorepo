from __future__ import annotations

import math
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

import requests

from core.model_catalog import get_model_spec

_DEFAULT_COMPLETION_BUDGET = 512
_SAFETY_MARGIN_TOKENS = 512
_MIN_SLM_AUTO_BUDGET = 128
_MIN_LLM_AUTO_BUDGET = 256


def compute_completion_budget(
    provider: Any,
    prompt: str,
    *,
    task_type: str,
    role: str,
    requested_max_tokens: int = 0,
) -> int:
    """Return an output-token budget that fits the prompt and task shape.

    Policy:
    - If `requested_max_tokens > 0`, treat it as an explicit override.
    - Otherwise use a task/role-specific default budget.
    - In auto mode, never go below separate SLM/LLM floor budgets unless the
      model context window leaves less room than that.
    - If the provider exposes a vLLM/OpenAI-compatible `/models` endpoint with
      `max_model_len`, clamp the result so prompt + output stays below that cap
      with a safety margin.
    """
    if requested_max_tokens > 0:
        desired = requested_max_tokens
    else:
        desired = max(
            _policy_default(task_type, role),
            _minimum_auto_budget(provider, role),
        )
    desired = max(1, desired)

    context_limit = _get_context_limit(provider)
    if context_limit is None:
        return desired

    prompt_tokens = _estimate_prompt_tokens(prompt)
    available = max(1, context_limit - prompt_tokens - _SAFETY_MARGIN_TOKENS)
    return max(1, min(desired, available))


def _policy_default(task_type: str, role: str) -> int:
    if task_type == "mcq":
        if role in {"proponent", "opponent"}:
            return 192
        if role in {"arbitrator"}:
            return 32
        return 32

    if role in {"proponent", "opponent"}:
        return 384
    if role in {"arbitrator"}:
        return 256
    if role in {"llm_fallback", "llm_tiebreak"}:
        return 512
    return 256


def _minimum_auto_budget(provider: Any, role: str) -> int:
    model_id = getattr(provider, "model_id", None)
    if isinstance(model_id, str):
        spec = get_model_spec(model_id)
        if spec is not None:
            return _MIN_SLM_AUTO_BUDGET if spec.kind == "slm" else _MIN_LLM_AUTO_BUDGET

    llm_roles = {
        "llm_fallback",
        "llm_tiebreak",
        "monolithic_llm",
    }
    slm_roles = {
        "slm_draft",
        "ensemble_member",
        "proponent",
        "opponent",
    }
    if role in llm_roles:
        return _MIN_LLM_AUTO_BUDGET
    if role in slm_roles:
        return _MIN_SLM_AUTO_BUDGET
    return _MIN_LLM_AUTO_BUDGET


def _estimate_prompt_tokens(prompt: str) -> int:
    # Cheap tokenizer-free approximation that is stable enough for budgeting.
    return max(1, math.ceil(len(prompt) / 4))


def _get_context_limit(provider: Any) -> int | None:
    base_url = getattr(provider, "base_url", None)
    model_id = getattr(provider, "model_id", None)
    if not isinstance(base_url, str) or not isinstance(model_id, str):
        return None
    parsed = urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        return None
    return _fetch_context_limit(base_url.rstrip("/"), model_id)


@lru_cache(maxsize=64)
def _fetch_context_limit(base_url: str, model_id: str) -> int | None:
    try:
        response = requests.get(f"{base_url}/models", timeout=5.0)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    data = payload.get("data", [])
    if not isinstance(data, list):
        return None

    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("id") != model_id:
            continue
        max_len = item.get("max_model_len")
        if isinstance(max_len, int) and max_len > 0:
            return max_len
    return None
