"""
Model provider abstractions.

All providers implement a common interface:
    generate(prompt: str, **kwargs) -> tuple[str, float, int, int, float]
    Returns: (text, confidence, input_tokens, output_tokens, cost_usd)
"""
from __future__ import annotations

import math
import os
from ipaddress import ip_address
from urllib.parse import urlparse
from abc import ABC, abstractmethod

import requests

from core.model_catalog import get_model_spec

# Per-token costs in USD (approximate, May 2026)
_APPROX_MODEL_COSTS: dict[str, tuple[float, float]] = {
    "openai/gpt-oss-120b": (1.80 / 1_000_000, 7.20 / 1_000_000),
    "meta-llama/Llama-3.3-70B-Instruct": (0.90 / 1_000_000, 0.90 / 1_000_000),
    "openai/gpt-oss-20b": (0.40 / 1_000_000, 1.60 / 1_000_000),
}


class ModelProvider(ABC):
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        """Returns (text, confidence, input_tokens, output_tokens, cost_usd)."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.model_id})"


class OllamaModel(ModelProvider):
    """Local Ollama model for the selected Qwen, Gemma, and Llama checkpoints."""

    def __init__(
        self,
        model_id: str,
        base_url: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", 512),
            },
        }
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        text = data.get("response", "").strip()
        input_tokens = data.get("prompt_eval_count", 0)
        output_tokens = data.get("eval_count", 0)

        # Confidence via token probability (Ollama returns logits optionally)
        confidence = self._estimate_confidence(data)
        return text, confidence, input_tokens, output_tokens, 0.0  # local = free

    def _estimate_confidence(self, data: dict) -> float:
        """
        Approximate confidence from eval duration ratio.
        If Ollama doesn't expose log-probs, we use a heuristic:
        short, fast responses tend to be higher-confidence.
        """
        eval_count = data.get("eval_count", 1) or 1
        eval_duration = data.get("eval_duration", 1) or 1
        tokens_per_ns = eval_count / eval_duration
        # Normalise to [0.3, 0.95] range
        raw = math.tanh(tokens_per_ns * 1e8)
        return max(0.3, min(0.95, raw))


class OpenAIModel(ModelProvider):
    """Generic OpenAI API wrapper kept for optional direct API experiments."""

    def __init__(
        self,
        model_id: str = "model",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        import openai
        client = openai.OpenAI(api_key=self.api_key)

        resp = client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", 512),
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
        self.api_key = api_key or os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
        self.temperature = temperature

    def generate(self, prompt: str, **kwargs) -> tuple[str, float, int, int, float]:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", 512),
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        text = data["choices"][0]["message"]["content"].strip()
        in_tok = data.get("usage", {}).get("prompt_tokens", 0)
        out_tok = data.get("usage", {}).get("completion_tokens", 0)
        in_cost, out_cost = _APPROX_MODEL_COSTS.get(self.model_id, (0.0, 0.0))
        cost = in_tok * in_cost + out_tok * out_cost

        return text, 0.8, in_tok, out_tok, cost


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
        payload = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", 512),
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
        text = choice["message"]["content"].strip()
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


def get_model(model_id: str) -> ModelProvider:
    """Factory — resolve selected-model aliases to the right runtime provider."""
    spec = get_model_spec(model_id)
    if spec is not None:
        if spec.provider == "ollama":
            if _force_openai_compatible(spec):
                base_url = os.getenv(spec.base_url_env or "", spec.base_url_default or "http://localhost:8000/v1")
                return OpenAICompatibleModel(
                    model_id=spec.openai_compatible_model or spec.provider_model,
                    base_url=base_url,
                )
            return OllamaModel(model_id=spec.provider_model)
        if spec.provider == "openai_compatible":
            base_url = os.getenv(spec.base_url_env or "", spec.base_url_default or "http://localhost:8000/v1")
            api_key = os.getenv(spec.api_key_env or "", "")
            return OpenAICompatibleModel(
                model_id=spec.provider_model,
                base_url=base_url,
                api_key=api_key,
            )

    return OllamaModel(model_id=model_id)


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

    if spec.provider == "ollama" and not _force_openai_compatible(spec):
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        return {
            "available": True,
            "provider": "ollama",
            "base_url": base_url,
            "reason": "Uses local Ollama endpoint.",
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
    try:
        if provider == "ollama":
            resp = requests.get(f"{base_url}/api/tags", timeout=timeout)
        elif provider == "openai_compatible":
            resp = requests.get(f"{base_url}/models", timeout=timeout)
        else:
            raise RuntimeError(f"Unsupported provider for {model_id}: {provider}")
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(
            f"{model_id} is configured for {provider} at {base_url}, but the endpoint is unreachable: {exc}"
        ) from exc


def _force_openai_compatible(spec) -> bool:
    if not spec.openai_compatible_model or not spec.base_url_env:
        return False

    force_vllm = os.getenv("THESIS_FORCE_VLLM", "").strip().lower()
    if force_vllm not in {"1", "true", "yes", "on"}:
        return False

    return bool(os.getenv(spec.base_url_env, spec.base_url_default or ""))


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
