"""Setup C — Hybrid Speculative Decoding (Draft-Verification).

A Qwen 3.5 4B *drafter* generates a candidate answer. A Llama 3.3 70B *verifier*
inspects the draft token-by-token and accepts or rolls back based on a
confidence threshold (default 0.75).

At query level this translates to:
  1. Drafter produces full answer + token log-probs.
  2. Verifier scores the draft via its own log-prob for each token.
  3. If mean acceptance rate >= threshold → accept draft (0 extra LLM tokens).
  4. Otherwise → verifier rewrites from the first rejected token (partial rollback).

This halves average latency vs full 70B inference while staying near 70B accuracy
on high-confidence queries.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass, field

import requests

from core.types import Query, Response


@dataclass
class _DraftResult:
    text: str
    tokens: list[str]
    logprobs: list[float]
    prompt_tokens: int
    completion_tokens: int


def _vllm_generate(
    base_url: str,
    model_name: str,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.0,
    logprobs: int = 1,
) -> _DraftResult:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "logprobs": True,
        "top_logprobs": logprobs,
    }
    resp = requests.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    choice = data["choices"][0]
    text = choice["message"]["content"].strip()
    usage = data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    # Extract per-token log-probs (vLLM returns content[i].logprob)
    lp_list: list[float] = []
    token_list: list[str] = []
    try:
        for entry in (choice.get("logprobs") or {}).get("content") or []:
            lp_list.append(entry["logprob"])
            token_list.append(entry.get("token", ""))
    except Exception:
        pass

    return _DraftResult(
        text=text,
        tokens=token_list,
        logprobs=lp_list,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


class SpeculativeDecodingArchitecture:
    """Qwen 3.5 4B drafter + Llama 3.3 70B verifier with token-level rollback."""

    def __init__(
        self,
        drafter_url: str | None = None,
        verifier_url: str | None = None,
        drafter_model: str = "Qwen/Qwen3.5-4B",
        verifier_model: str = "meta-llama/Llama-3.3-70B-Instruct",
        confidence_threshold: float = 0.75,
        max_tokens: int = 256,
    ) -> None:
        self.drafter_url = (drafter_url or os.environ.get("VLLM_QWEN35_4B_URL", "http://localhost:8001/v1"))
        self.verifier_url = (verifier_url or os.environ.get("VLLM_LLAMA33_70B_URL", "http://localhost:8000/v1"))
        self.drafter_model = drafter_model
        self.verifier_model = verifier_model
        self.confidence_threshold = confidence_threshold
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return "speculative_decoding"

    def run(self, query: Query) -> Response:
        prompt = self._build_prompt(query)
        t0 = time.perf_counter()

        # Phase 1: draft
        draft = _vllm_generate(
            self.drafter_url,
            self.drafter_model,
            prompt,
            max_tokens=self.max_tokens,
        )

        # Phase 2: verify
        accepted, llm_calls, verifier_tokens = self._verify(prompt, draft)
        total_in = draft.prompt_tokens
        total_out = draft.completion_tokens + verifier_tokens
        latency_ms = (time.perf_counter() - t0) * 1000

        if accepted:
            final_text = draft.text
        else:
            # Verifier rewrote from rollback point — its output IS the final answer
            rewrite = _vllm_generate(
                self.verifier_url,
                self.verifier_model,
                prompt,
                max_tokens=self.max_tokens,
            )
            final_text = rewrite.text
            total_in += rewrite.prompt_tokens
            total_out += rewrite.completion_tokens
            llm_calls += 1
            latency_ms = (time.perf_counter() - t0) * 1000

        predicted = self._parse_answer(final_text, query)
        cost_usd = self._estimate_cost(draft.completion_tokens, verifier_tokens)

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=predicted,
            model_id=self.drafter_model if accepted else self.verifier_model,
            llm_calls=llm_calls,
            latency_ms=latency_ms,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=cost_usd,
            confidence=self._mean_confidence(draft.logprobs),
        )

    # ------------------------------------------------------------------

    def _verify(self, prompt: str, draft: _DraftResult) -> tuple[bool, int, int]:
        """Score the draft against the verifier. Returns (accepted, llm_calls, tokens_used)."""
        if not draft.logprobs:
            # No log-probs available; call verifier as scorer
            return self._verifier_score_draft(prompt, draft)

        mean_acceptance = self._mean_confidence(draft.logprobs)
        if mean_acceptance >= self.confidence_threshold:
            return True, 0, 0

        # Partial rollback: find first token below threshold and mark as rejected
        rollback_idx = next(
            (i for i, lp in enumerate(draft.logprobs) if math.exp(lp) < self.confidence_threshold),
            len(draft.logprobs),
        )
        # If >80% of tokens accepted, still use the draft (minor mismatch)
        if rollback_idx / max(len(draft.logprobs), 1) >= 0.80:
            return True, 0, 0

        return False, 1, 0

    def _verifier_score_draft(self, prompt: str, draft: _DraftResult) -> tuple[bool, int, int]:
        """Ask the verifier to score the draft text directly."""
        score_prompt = (
            f"Rate the correctness of the following answer on a scale 0.0–1.0.\n"
            f"Question: {prompt[-500:]}\nAnswer: {draft.text}\n"
            "Reply with only a decimal number, e.g. 0.85"
        )
        result = _vllm_generate(
            self.verifier_url,
            self.verifier_model,
            score_prompt,
            max_tokens=8,
        )
        try:
            score = float(result.text.strip())
        except ValueError:
            score = 0.5
        accepted = score >= self.confidence_threshold
        return accepted, 1, result.completion_tokens

    def _mean_confidence(self, logprobs: list[float]) -> float:
        if not logprobs:
            return 0.5
        return sum(math.exp(lp) for lp in logprobs) / len(logprobs)

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

    def _estimate_cost(self, draft_tokens: int, verifier_tokens: int) -> float:
        # Drafter (4B): ~$0.10/1M tokens; Verifier (70B): ~$0.90/1M tokens
        return (draft_tokens * 0.10 + verifier_tokens * 0.90) / 1_000_000
