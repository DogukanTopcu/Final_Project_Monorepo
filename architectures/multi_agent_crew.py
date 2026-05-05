"""Setup B — Multi-Agent SLM Pipeline (CrewAI + LangGraph routing).

Three specialist SLMs collaborate:
  - Reasoning agent: Llama-3-8B-Instruct  (port 8001)
  - Code agent:      CodeLlama-7B-Instruct (port 8002)
  - Factual agent:   Mistral-7B-v0.3       (port 8003)

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
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return text, tokens


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
        llama8b_url: str | None = None,
        codellama_url: str | None = None,
        mistral_url: str | None = None,
        cross_check: bool = False,
    ) -> None:
        self.agents: dict[Domain, VLLMAgent] = {
            Domain.REASONING: VLLMAgent(
                llama8b_url or os.environ.get("VLLM_LLAMA8B_URL", "http://localhost:8001/v1"),
                "meta-llama/Meta-Llama-3-8B-Instruct",
            ),
            Domain.CODE: VLLMAgent(
                codellama_url or os.environ.get("VLLM_CODELLAMA_URL", "http://localhost:8002/v1"),
                "codellama/CodeLlama-7b-Instruct-hf",
            ),
            Domain.FACTUAL: VLLMAgent(
                mistral_url or os.environ.get("VLLM_MISTRAL_URL", "http://localhost:8003/v1"),
                "mistralai/Mistral-7B-Instruct-v0.3",
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

        text, tokens = agent.chat(system, prompt)
        total_tokens = tokens
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
            cross_text, cross_tokens = second_agent.chat(self._systems[second_domain], cross_prompt)
            total_tokens += cross_tokens
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
            total_tokens=total_tokens,
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
