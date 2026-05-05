"""Setup A — Monolithic Llama-3-70B-Instruct (single-pass baseline).

Calls a locally-served vLLM endpoint (OpenAI-compatible). Every query goes
directly to the 70B model; there is no routing or agent layer. This establishes
the accuracy and cost ceiling against which Setups B and C are compared.
"""
from __future__ import annotations

import os
import time

import requests

from core.types import Query, Response


class MonolithicArchitecture:
    """Single-pass Llama-3-70B via vLLM OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str = "meta-llama/Meta-Llama-3-70B-Instruct",
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> None:
        self.base_url = (base_url or os.environ.get("VLLM_LLAMA70B_URL", "http://localhost:8000/v1")).rstrip("/")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return "monolithic_70b"

    def run(self, query: Query) -> Response:
        prompt = self._build_prompt(query)
        t0 = time.perf_counter()
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "logprobs": True,
            "top_logprobs": 1,
        }
        resp = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=120)
        resp.raise_for_status()
        latency_ms = (time.perf_counter() - t0) * 1000

        data = resp.json()
        choice = data["choices"][0]
        text = choice["message"]["content"].strip()
        usage = data.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        confidence = self._extract_confidence(choice)
        predicted = self._parse_answer(text, query)
        cost_usd = self._estimate_cost(prompt_tokens, completion_tokens)

        return Response(
            query_id=query.id,
            text=text,
            predicted_answer=predicted,
            model_id=self.model_name,
            llm_calls=1,
            latency_ms=latency_ms,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, query: Query) -> str:
        from core.prompt import mcq_prompt, open_prompt
        if query.choices:
            return mcq_prompt(query)
        return open_prompt(query)

    def _extract_confidence(self, choice: dict) -> float:
        try:
            logprobs = choice.get("logprobs", {}) or {}
            content = logprobs.get("content") or []
            if content:
                import math
                return math.exp(content[0]["logprob"])
        except Exception:
            pass
        return 1.0

    def _parse_answer(self, text: str, query: Query) -> str:
        from core.prompt import parse_mcq_answer, parse_open_answer
        if query.choices:
            return parse_mcq_answer(text)
        return parse_open_answer(text)

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Self-hosted vLLM: cost is essentially compute time; approximate
        # using Together AI pricing for Llama-3-70B as a reference
        # $0.90 per 1M input tokens, $0.90 per 1M output tokens
        return (prompt_tokens * 0.90 + completion_tokens * 0.90) / 1_000_000
