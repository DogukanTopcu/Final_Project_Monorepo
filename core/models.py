"""
Model provider abstractions.

All providers implement a common interface:
    generate(prompt: str, **kwargs) -> tuple[str, float, int, int, float]
    Returns: (text, confidence, input_tokens, output_tokens, cost_usd)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from ipaddress import ip_address
import math
import os
from urllib.parse import urlparse

import requests

from core.model_catalog import (
    get_expected_runtime_model_ids,
    get_model_spec,
    get_served_model_id,
)
from core.token_budget import compute_completion_budget

# Per-token costs in USD (approximate, May 2026)
_APPROX_MODEL_COSTS: dict[str, tuple[float, float]] = {
    "openai/gpt-oss-120b": (1.80 / 1_000_000, 7.20 / 1_000_000),
    "meta-llama/Llama-3.3-70B-Instruct": (0.90 / 1_000_000, 0.90 / 1_000_000),
    "openai/gpt-oss-20b": (0.40 / 1_000_000, 1.60 / 1_000_000),
}

_GEMINI_COSTS: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash": (0.30 / 1_000_000, 2.50 / 1_000_000),
    "gemini-2.5-flash-lite": (0.10 / 1_000_000, 0.40 / 1_000_000),
}

_DEFAULT_MAX_TOKENS = 512


def _get_env(*names: str, default: str = "") -> str:
    """Return the first non-empty environment variable from the given names."""
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default


def _extract_message_text(message: object) -> str:
    """Normalize OpenAI-compatible message payloads into plain text.

    Some reasoning-capable models return `message.content=None` and place the
    visible answer in a structured content list instead of a raw string.
    """
    if isinstance(message, str):
        return message.strip()
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text)
                continue
            nested_text = item.get("content")
            if isinstance(nested_text, str) and nested_text.strip():
                parts.append(nested_text)
        return "\n".join(part.strip() for part in parts if part and part.strip()).strip()

    refusal = message.get("refusal")
    if isinstance(refusal, str):
        return refusal.strip()

    return ""


def _resolve_max_tokens(provider: "ModelProvider", prompt: str, kwargs: dict) -> int:
    requested = kwargs.get("max_tokens", 0)
    if not isinstance(requested, int):
        requested = _DEFAULT_MAX_TOKENS
    return compute_completion_budget(
        provider,
        prompt,
        task_type=str(kwargs.get("task_type", "open")),
        role=str(kwargs.get("role", "direct")),
        requested_max_tokens=requested,
    )


class ModelProvider(ABC):
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        """Returns (text, confidence, input_tokens, output_tokens, cost_usd)."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.model_id})"


class OpenAIModel(ModelProvider):
    """Generic OpenAI API wrapper kept for optional direct API experiments."""

    def __init__(
        self,
        model_id: str = "model",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or _get_env(
            "THESIS_OPENAI_API_KEY",
            "OPENAI_COMPATIBLE_API_KEY",
        )
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        max_tokens = _resolve_max_tokens(self, prompt, kwargs)

        resp = client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=max_tokens,
            logprobs=True,
            top_logprobs=1,
        )

        choice = resp.choices[0]
        text = choice.message.content or ""
        usage = resp.usage
        in_tok = usage.prompt_tokens
        out_tok = usage.completion_tokens

        in_cost, out_cost = _APPROX_MODEL_COSTS.get(self.model_id, (0.0, 0.0))
        cost = in_tok * in_cost + out_tok * out_cost

        confidence = self._logprob_confidence(choice)
        return text.strip(), confidence, in_tok, out_tok, cost

    @staticmethod
    def _logprob_confidence(choice) -> float:
        """Mean token probability from first few output tokens."""
        try:
            lp_content = choice.logprobs.content or []
            if not lp_content:
                return 0.5
            log_probs = [t.logprob for t in lp_content[:10] if t.logprob is not None]
            if not log_probs:
                return 0.5
            avg_lp = sum(log_probs) / len(log_probs)
            return float(math.exp(avg_lp))
        except Exception:
            return 0.5


class TogetherModel(ModelProvider):
    """Generic Together-compatible wrapper kept for optional hosted inference."""

    def __init__(
        self,
        model_id: str = "model",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or _get_env(
            "THESIS_TOGETHER_API_KEY",
            "OPENAI_COMPATIBLE_API_KEY",
        )
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        url = "https://api.together.xyz/v1/chat/completions"
        max_tokens = _resolve_max_tokens(self, prompt, kwargs)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": max_tokens,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        text = _extract_message_text(data["choices"][0]["message"])
        in_tok = data.get("usage", {}).get("prompt_tokens", 0)
        out_tok = data.get("usage", {}).get("completion_tokens", 0)
        in_cost, out_cost = _APPROX_MODEL_COSTS.get(self.model_id, (0.0, 0.0))
        cost = in_tok * in_cost + out_tok * out_cost

        return text, 0.8, in_tok, out_tok, cost


class GeminiModel(ModelProvider):
    """Gemini Developer API via the official OpenAI-compatible endpoint."""

    def __init__(
        self,
        model_id: str = "gemini-2.5-flash",
        api_key: str | None = None,
        temperature: float = 0.0,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or _get_env(
            "THESIS_GEMINI_API_KEY",
            "GEMINI_API_KEY",
        )
        self.temperature = temperature
        self.base_url = base_url

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        import openai
        max_tokens = _resolve_max_tokens(self, prompt, kwargs)

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        response = client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        text = choice.message.content or ""
        usage = response.usage
        in_tok = usage.prompt_tokens if usage is not None else 0
        out_tok = usage.completion_tokens if usage is not None else 0

        in_cost, out_cost = _GEMINI_COSTS.get(self.model_id, (0.0, 0.0))
        cost = in_tok * in_cost + out_tok * out_cost

        return text.strip(), 0.5, in_tok, out_tok, cost


class OpenAICompatibleModel(ModelProvider):
    """OpenAI-compatible HTTP endpoint wrapper for vLLM and hosted gateways."""

    def __init__(
        self,
        model_id: str,
        base_url: str,
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.temperature = temperature
        self._local_endpoint = _is_local_or_private_endpoint(self.base_url)

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        max_tokens = _resolve_max_tokens(self, prompt, kwargs)
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": max_tokens,
            "logprobs": True,
            "top_logprobs": 1,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        text = _extract_message_text(choice["message"])
        usage = data.get("usage", {})
        in_tok = usage.get("prompt_tokens", 0)
        out_tok = usage.get("completion_tokens", 0)
        cost = 0.0
        if not self._local_endpoint:
            in_cost, out_cost = _APPROX_MODEL_COSTS.get(self.model_id, (0.0, 0.0))
            cost = in_tok * in_cost + out_tok * out_cost

        confidence = self._logprob_confidence(choice)
        return text, confidence, in_tok, out_tok, cost

    @staticmethod
    def _logprob_confidence(choice: dict) -> float:
        try:
            content = (choice.get("logprobs") or {}).get("content") or []
            log_probs = [token["logprob"] for token in content[:10] if token.get("logprob") is not None]
            if not log_probs:
                return 0.5
            return float(math.exp(sum(log_probs) / len(log_probs)))
        except Exception:
            return 0.5
_GEMINI_MAP = {
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
}


def get_model(model_id: str) -> ModelProvider:
    """Factory — resolve selected-model aliases to the right runtime provider."""
    spec = get_model_spec(model_id)
    if spec is not None:
        if spec.provider == "openai_compatible":
            base_url = os.getenv(spec.base_url_env or "", spec.base_url_default or "http://localhost:8000/v1")
            api_key = os.getenv(spec.api_key_env or "", "")
            return OpenAICompatibleModel(
                model_id=get_served_model_id(model_id) or spec.provider_model,
                base_url=base_url,
                api_key=api_key,
            )
        raise ValueError(f"Unsupported provider '{spec.provider}' for {model_id}.")

    if model_id in _GEMINI_MAP:
        return GeminiModel(model_id=_GEMINI_MAP[model_id])

    raise ValueError(f"Unknown model alias: {model_id}")


def get_model_runtime_status(model_id: str) -> dict[str, str | bool]:
    """
    Return the resolved runtime shape for a model alias.

    This is intentionally lightweight and config-driven. It answers:
    - which provider would be used right now
    - which endpoint/key envs are relevant
    - whether the current config is sufficient to attempt a call
    """
    spec = get_model_spec(model_id)
    if spec is None:
        return {
            "available": False,
            "provider": "unknown",
            "reason": f"Unknown model alias: {model_id}",
        }

    base_url = os.getenv(spec.base_url_env or "", spec.base_url_default or "").rstrip("/")
    if not base_url:
        return {
            "available": False,
            "provider": "openai_compatible",
            "reason": f"No endpoint configured for {model_id}.",
        }

    api_key = os.getenv(spec.api_key_env or "", "")
    key_required = bool(spec.api_key_env) and not _is_local_or_private_endpoint(base_url)
    if key_required and not api_key:
        return {
            "available": False,
            "provider": "openai_compatible",
            "base_url": base_url,
            "reason": f"{model_id} targets a remote OpenAI-compatible endpoint and requires {spec.api_key_env}.",
        }

    return {
        "available": True,
        "provider": "openai_compatible",
        "base_url": base_url,
        "reason": "Uses an OpenAI-compatible endpoint.",
    }


def assert_model_runnable(model_id: str, timeout: float = 3.0) -> None:
    """
    Fail early with a clear message if the resolved runtime is unreachable.
    """
    status = get_model_runtime_status(model_id)
    if not bool(status.get("available")):
        raise RuntimeError(str(status.get("reason", f"Model {model_id} is unavailable.")))

    provider = str(status.get("provider", "unknown"))
    base_url = str(status.get("base_url", ""))
    spec = get_model_spec(model_id)
    try:
        if provider != "openai_compatible":
            raise RuntimeError(f"Unsupported provider for {model_id}: {provider}")
        resp = requests.get(f"{base_url}/models", timeout=timeout)
        resp.raise_for_status()
        if spec is not None:
            payload = resp.json()
            served = {
                item.get("id")
                for item in payload.get("data", [])
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            expected = get_expected_runtime_model_ids(model_id)
            if served.isdisjoint(expected):
                raise RuntimeError(
                    f"{model_id} expects one of {sorted(expected)} at {base_url}, "
                    f"but the endpoint currently serves {sorted(served) or ['<none>']}."
                )
            probe_model_id = get_served_model_id(model_id) or spec.provider_model
            probe_payload = {
                "model": probe_model_id,
                "messages": [{"role": "user", "content": "Ping"}],
                "temperature": 0,
                "max_tokens": 1,
            }
            probe = requests.post(
                f"{base_url}/chat/completions",
                json=probe_payload,
                timeout=max(timeout, 10.0),
            )
            probe.raise_for_status()
    except Exception as exc:
        raise RuntimeError(
            f"{model_id} is configured for {provider} at {base_url}, but the runtime check failed: {exc}"
        ) from exc


def _is_local_or_private_endpoint(base_url: str) -> bool:
    hostname = urlparse(base_url).hostname
    if hostname is None:
        return False
    if hostname in {"localhost", "127.0.0.1"}:
        return True
    try:
        parsed_ip = ip_address(hostname)
    except ValueError:
        return hostname.endswith(".internal")
    return parsed_ip.is_private or parsed_ip.is_loopback
