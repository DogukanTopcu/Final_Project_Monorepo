"""
Model provider abstractions.

All providers implement a common interface:
    generate(prompt: str, **kwargs) -> tuple[str, float, int, int, float]
    Returns: (text, confidence, input_tokens, output_tokens, cost_usd)
"""
from __future__ import annotations

import math
import os
import time
from abc import ABC, abstractmethod

import requests

# Per-token costs in USD (approximate, May 2026)
_OPENAI_COSTS: dict[str, tuple[float, float]] = {
    "gpt-4o":      (2.50 / 1_000_000, 10.00 / 1_000_000),
    "gpt-4o-mini": (0.15 / 1_000_000,  0.60 / 1_000_000),
}
_TOGETHER_COSTS: dict[str, tuple[float, float]] = {
    "meta-llama/Llama-3-70b-chat-hf": (0.90 / 1_000_000, 0.90 / 1_000_000),
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
    """Local Ollama SLM — Phi-3 Mini, Qwen2.5, Llama 3.2, etc."""

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
    """OpenAI API — GPT-4o, GPT-4o mini."""

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
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

        in_cost, out_cost = _OPENAI_COSTS.get(self.model_id, (0.0, 0.0))
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
    """Together AI — Llama 3 70B and others."""

    def __init__(
        self,
        model_id: str = "meta-llama/Llama-3-70b-chat-hf",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        super().__init__(model_id)
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY", "")
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
        in_cost, out_cost = _TOGETHER_COSTS.get(self.model_id, (0.0, 0.0))
        cost = in_tok * in_cost + out_tok * out_cost

        return text, 0.8, in_tok, out_tok, cost


_OLLAMA_MAP = {
    "phi3-mini":    "phi3:mini",
    "qwen2.5-1.5b": "qwen2.5:1.5b",
    "qwen2.5-7b":   "qwen2.5:7b",
    "llama3.2-3b":  "llama3.2:3b",
}

_OPENAI_MAP = {
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-4o":      "gpt-4o",
}

_TOGETHER_MAP = {
    "llama3-70b": "meta-llama/Llama-3-70b-chat-hf",
}


def get_model(model_id: str) -> ModelProvider:
    """Factory — resolve friendly name to a ModelProvider instance."""
    if model_id in _OPENAI_MAP:
        return OpenAIModel(model_id=_OPENAI_MAP[model_id])
    if model_id in _TOGETHER_MAP:
        return TogetherModel(model_id=_TOGETHER_MAP[model_id])
    ollama_name = _OLLAMA_MAP.get(model_id, model_id)
    return OllamaModel(model_id=ollama_name)
