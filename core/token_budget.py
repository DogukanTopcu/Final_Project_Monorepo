from __future__ import annotations

from functools import lru_cache
import math
from typing import Any
from urllib.parse import urlparse

import requests


_DEFAULT_COMPLETION_BUDGET = 512
_SAFETY_MARGIN_TOKENS = 512


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
    - If the provider exposes a vLLM/OpenAI-compatible `/models` endpoint with
      `max_model_len`, clamp the result so prompt + output stays below that cap
      with a safety margin.
    """
    desired = requested_max_tokens if requested_max_tokens > 0 else _policy_default(task_type, role)
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
