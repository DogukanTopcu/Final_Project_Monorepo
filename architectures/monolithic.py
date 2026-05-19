"""Setup A — Monolithic single-LLM baseline.

Every query goes directly to the selected heavy baseline model; there is no
routing or agent layer. This establishes the accuracy/cost ceiling against
which the other architectures are compared.

Supports two construction modes:
  - `MonolithicArchitecture(llm=ModelProvider, ...)` — preferred path used by
    the experiment runner. The provider may target any LLM in the catalog.
  - `MonolithicArchitecture(base_url=..., model_name=...)` — direct vLLM
    construction kept for backwards compatibility with older callers.
"""
from __future__ import annotations

import math
import os
import time

import requests

from core.models import ModelProvider, OpenAICompatibleModel
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


class MonolithicArchitecture:
    """Single-pass LLM baseline."""

    name = "monolithic"

    def __init__(
        self,
        llm: ModelProvider | None = None,
        slm: ModelProvider | None = None,  # ignored; accepted for runner uniformity
        base_url: str | None = None,
        model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
        temperature: float = 0.0,
        max_tokens: int = 0,
        task_type: str = "mcq",
        # Accept (and ignore) the common runner kwargs so callers can pass them
        # without having to special-case monolithic.
        slm_temperature: float | None = None,
        slm_max_tokens: int | None = None,
        llm_temperature: float | None = None,
        llm_max_tokens: int | None = None,
    ) -> None:
        self.task_type = task_type
        self.temperature = (
            llm_temperature if llm_temperature is not None else temperature
        )
        self.max_tokens = (
            llm_max_tokens if llm_max_tokens is not None else max_tokens
        )
        self.slm = slm  # unused; preserved for runner symmetry

        if llm is not None:
            self.llm = llm
            self.model_name = llm.model_id
            self.base_url = getattr(llm, "base_url", base_url) or ""
            self._use_provider = True
        else:
            self.base_url = (
                base_url or os.environ.get("VLLM_LLAMA33_70B_URL", "http://localhost:8000/v1")
            ).rstrip("/")
            self.model_name = model_name
            self.llm = OpenAICompatibleModel(model_id=model_name, base_url=self.base_url)
            self._use_provider = False

    def run(self, query: Query) -> Response:
        prompt = self._build_prompt(query)

        if self._use_provider:
            return self._run_via_provider(query, prompt)
        return self._run_via_http(query, prompt)

    # ------------------------------------------------------------------
    # Execution paths
    # ------------------------------------------------------------------

    def _run_via_provider(self, query: Query, prompt: str) -> Response:
        budget = compute_completion_budget(
            self.llm,
            prompt,
            task_type=self.task_type,
            role="monolithic_llm",
            requested_max_tokens=self.max_tokens,
        )
        t0 = time.perf_counter()
        text, conf, in_t, out_t, cost = self.llm.generate(
            prompt,
            temperature=self.temperature,
            max_tokens=budget,
        )
        latency_ms = (time.perf_counter() - t0) * 1000.0

        predicted = self._parse_answer(text, query)
        return Response(
            query_id=query.id,
            text=text,
            predicted_answer=predicted,
            model_id=self.llm.model_id,
            llm_calls=1,
            latency_ms=latency_ms,
            input_tokens=in_t,
            output_tokens=out_t,
            cost_usd=cost,
            confidence=conf,
            metadata={
                "inference_steps": [
                    {
                        "role": "monolithic_llm",
                        "model_id": self.llm.model_id,
                        "latency_ms": latency_ms,
                        "input_tokens": in_t,
                        "output_tokens": out_t,
                        "api_cost_usd": cost,
                    }
                ]
            },
        )

    def _run_via_http(self, query: Query, prompt: str) -> Response:
        budget = compute_completion_budget(
            self.llm,
            prompt,
            task_type=self.task_type,
            role="monolithic_llm",
            requested_max_tokens=self.max_tokens,
        )
        t0 = time.perf_counter()
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": budget,
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
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            cost_usd=cost_usd,
            confidence=confidence,
            metadata={
                "inference_steps": [
                    {
                        "role": "monolithic_llm",
                        "model_id": self.model_name,
                        "latency_ms": latency_ms,
                        "input_tokens": prompt_tokens,
                        "output_tokens": completion_tokens,
                        "api_cost_usd": cost_usd,
                    }
                ]
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, query: Query) -> str:
        if query.choices:
            return mcq_prompt(query)
        return open_prompt(query)

    def _extract_confidence(self, choice: dict) -> float:
        try:
            logprobs = choice.get("logprobs", {}) or {}
            content = logprobs.get("content") or []
            if content:
                return math.exp(content[0]["logprob"])
        except Exception:
            pass
        return 1.0

    def _parse_answer(self, text: str, query: Query) -> str | None:
        if query.choices:
            return parse_mcq_answer(text)
        return parse_open_answer(text)

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return (prompt_tokens * 0.90 + completion_tokens * 0.90) / 1_000_000
