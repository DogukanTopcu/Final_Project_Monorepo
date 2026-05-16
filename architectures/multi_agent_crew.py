"""Setup B — Multi-Agent SLM Pipeline (CrewAI + LangGraph routing).

Three specialist SLMs collaborate:
  - Reasoning agent: Qwen 3.5 4B   (port 8001)
  - Code agent:      Gemma 4 E4B   (port 8002)
  - Factual agent:   Llama 3.2 3B  (port 8003)

LangGraph routes each query to the best-fit agent based on domain
classification, then optionally cross-checks via a second agent.
The final answer is extracted from the agent's response.

No external LLM calls are made — all models are self-hosted on L40S.
"""
from __future__ import annotations

import os
import re
import time
from enum import Enum
from typing import Any

import requests

from core.types import Query, Response


class Domain(str, Enum):
    REASONING = "reasoning"
    CODE = "code"
    FACTUAL = "factual"


class VLLMAgent:
    """Thin wrapper around a vLLM OpenAI-compatible endpoint."""

    def __init__(self, base_url: str, model_name: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def chat(self, system: str, user: str, max_tokens: int = 512, temperature: float = 0.0) -> tuple[str, float]:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        usage = data.get("usage", {})
        return (
            text,
            usage.get("prompt_tokens", 0),
            usage.get("completion_tokens", 0),
        )


def _classify_domain(query: Query) -> Domain:
    """Heuristic domain classifier based on query text."""
    text_lower = query.text.lower()
    code_keywords = {"code", "function", "program", "algorithm", "python", "implement", "debug", "compile", "syntax"}
    if any(k in text_lower for k in code_keywords):
        return Domain.CODE
    math_keywords = {"calculate", "solve", "equation", "proof", "derive", "integral", "theorem", "geometry"}
    if any(k in text_lower for k in math_keywords) or re.search(r"\d+\s*[\+\-\*/\^]\s*\d+", text_lower):
        return Domain.REASONING
    return Domain.FACTUAL


_SYSTEM_REASONING = (
    "You are an expert reasoning assistant. Solve step-by-step. "
    "End your answer with 'Final Answer: <letter>' for MCQ or a number for math."
)
_SYSTEM_CODE = (
    "You are an expert programming assistant. Produce correct, concise code. "
    "End your answer with 'Final Answer: <letter>' for MCQ or the function for code generation."
)
_SYSTEM_FACTUAL = (
    "You are a knowledgeable assistant with broad factual expertise. "
    "End your answer with 'Final Answer: <letter>' for MCQ."
)


class MultiAgentCrewArchitecture:
    """LangGraph-routed CrewAI multi-agent pipeline."""

    def __init__(
        self,
        qwen4b_url: str | None = None,
        gemma4e4b_url: str | None = None,
        llama32_3b_url: str | None = None,
        legacy_reasoning_url: str | None = None,
        legacy_code_url: str | None = None,
        legacy_factual_url: str | None = None,
        cross_check: bool = False,
    ) -> None:
        self.agents: dict[Domain, VLLMAgent] = {
            Domain.REASONING: VLLMAgent(
                qwen4b_url or legacy_reasoning_url or os.environ.get("VLLM_QWEN35_4B_URL", "http://localhost:8001/v1"),
                "Qwen/Qwen3.5-4B",
            ),
            Domain.CODE: VLLMAgent(
                gemma4e4b_url or legacy_code_url or os.environ.get("VLLM_GEMMA4_E4B_URL", "http://localhost:8002/v1"),
                "google/gemma-4-E4B-it",
            ),
            Domain.FACTUAL: VLLMAgent(
                llama32_3b_url or legacy_factual_url or os.environ.get("VLLM_LLAMA32_3B_URL", "http://localhost:8003/v1"),
                "meta-llama/Llama-3.2-3B-Instruct",
            ),
        }
        self.cross_check = cross_check
        self._systems: dict[Domain, str] = {
            Domain.REASONING: _SYSTEM_REASONING,
            Domain.CODE: _SYSTEM_CODE,
            Domain.FACTUAL: _SYSTEM_FACTUAL,
        }

    @property
    def name(self) -> str:
        return "multi_agent_crew"

    def run(self, query: Query) -> Response:
        t0 = time.perf_counter()
        domain = _classify_domain(query)
        agent = self.agents[domain]
        system = self._systems[domain]
        prompt = self._build_prompt(query)

        text, prompt_tokens, completion_tokens = agent.chat(system, prompt)
        total_in = prompt_tokens
        total_out = completion_tokens
        llm_calls = 0  # all are SLMs

        if self.cross_check:
            # Route to a second agent for factual cross-check
            second_domain = Domain.FACTUAL if domain != Domain.FACTUAL else Domain.REASONING
            second_agent = self.agents[second_domain]
            cross_prompt = (
                f"The following answer was given to a question. Verify and correct if needed.\n"
                f"Question: {query.text}\nAnswer: {text}\n"
                "Reply with 'Confirmed: <answer>' or 'Correction: <new answer>'."
            )
            cross_text, cross_in, cross_out = second_agent.chat(self._systems[second_domain], cross_prompt)
            total_in += cross_in
            total_out += cross_out
            if cross_text.lower().startswith("correction:"):
                text = cross_text.split(":", 1)[1].strip()

        latency_ms = (time.perf_counter() - t0) * 1000
        predicted = self._parse_answer(text, query)

        return Response(
            query_id=query.id,
            text=text,
            predicted_answer=predicted,
            model_id=agent.model_name,
            llm_calls=llm_calls,
            latency_ms=latency_ms,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=0.0,
            confidence=0.8,
        )

    def _build_prompt(self, query: Query) -> str:
        from core.prompt import mcq_prompt, open_prompt
        if query.choices:
            return mcq_prompt(query)
        return open_prompt(query)

    def _parse_answer(self, text: str, query: Query) -> str:
        from core.prompt import parse_mcq_answer, parse_open_answer
        if query.choices:
            return parse_mcq_answer(text)
        return parse_open_answer(text)
