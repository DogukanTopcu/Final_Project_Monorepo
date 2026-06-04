"""Hybrid speculative decoding with incremental verifier continuation.

The drafter proposes a full answer cheaply. The verifier then validates the
draft incrementally by continuing the accepted assistant prefix in small
windows. As long as the verifier keeps matching the draft prefix, we accept
that portion. On the first divergence, the verifier rewrites the remaining
suffix from the exact accepted prefix.

This is not tokenizer-coupled speculative decoding because the drafter and
verifier may use different tokenizers. Instead, it implements the same
behavioral contract at the text-prefix level:

1. Draft the answer with the SLM.
2. Verify the draft incrementally from left to right.
3. Accept the longest verified prefix.
4. Rewrite only the rejected suffix with the LLM.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass

import requests

from core.models import (
    ModelProvider,
    OpenAICompatibleModel,
    _is_local_or_private_endpoint,
)
from core.prompt import build_prompt, parse_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response

_APPROX_MODEL_COSTS: dict[str, tuple[float, float]] = {
    "Qwen/Qwen3.5-4B": (0.10 / 1_000_000, 0.10 / 1_000_000),
    "qwen3.5-4b": (0.10 / 1_000_000, 0.10 / 1_000_000),
    "meta-llama/Llama-3.3-70B-Instruct": (0.90 / 1_000_000, 0.90 / 1_000_000),
    "llama3.3-70b": (0.90 / 1_000_000, 0.90 / 1_000_000),
}


@dataclass
class _GenerationResult:
    text: str
    tokens: list[str]
    logprobs: list[float]
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    finish_reason: str | None = None
    continuation_fallback_used: bool = False


def _is_qwen35_model(model_id: str) -> bool:
    normalized = model_id.strip().lower()
    return normalized.startswith("qwen/qwen3.5-") or normalized.startswith("qwen3.5-")


def _messages(prompt: str, accepted_prefix: str) -> list[dict[str, str]]:
    items = [{"role": "user", "content": prompt}]
    if accepted_prefix:
        items.append({"role": "assistant", "content": accepted_prefix})
    return items


def _continuation_fallback_messages(prompt: str, accepted_prefix: str) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": (
                "Continue the partial assistant answer from the exact point where it stopped.\n"
                "Do not repeat, restate, or paraphrase the accepted prefix.\n"
                "Output only the continuation that should come after the prefix.\n\n"
                f"Original user request:\n{prompt}\n\n"
                f"Accepted prefix:\n{accepted_prefix}"
            ),
        }
    ]


def _common_prefix_length(left: str, right: str) -> int:
    limit = min(len(left), len(right))
    idx = 0
    while idx < limit and left[idx] == right[idx]:
        idx += 1
    return idx


def _mean_confidence(logprobs: list[float]) -> float:
    if not logprobs:
        return 0.5
    return sum(math.exp(lp) for lp in logprobs) / len(logprobs)


def _estimate_cost(
    model_id: str,
    *,
    prompt_tokens: int,
    completion_tokens: int,
    local_endpoint: bool,
) -> float:
    if local_endpoint:
        return 0.0
    in_cost, out_cost = _APPROX_MODEL_COSTS.get(model_id, (0.0, 0.0))
    return prompt_tokens * in_cost + completion_tokens * out_cost


class SpeculativeDecodingArchitecture:
    name = "speculative"

    def __init__(
        self,
        drafter_url: str | None = None,
        verifier_url: str | None = None,
        drafter_model: str = "Qwen/Qwen3.5-4B",
        verifier_model: str = "meta-llama/Llama-3.3-70B-Instruct",
        confidence_threshold: float = 0.75,
        acceptance_threshold: float | None = None,
        max_tokens: int = 0,
        slm: ModelProvider | None = None,
        llm: ModelProvider | None = None,
        slm_temperature: float | None = None,
        llm_temperature: float | None = None,
        slm_max_tokens: int | None = None,
        llm_max_tokens: int | None = None,
        task_type: str | None = None,
        verifier_lookahead_tokens: int = 8,
    ) -> None:
        self.drafter = slm or OpenAICompatibleModel(
            model_id=drafter_model,
            base_url=(
                drafter_url or os.environ.get("VLLM_QWEN35_4B_URL", "http://localhost:8001/v1")
            ),
        )
        self.verifier = llm or OpenAICompatibleModel(
            model_id=verifier_model,
            base_url=(
                verifier_url or os.environ.get("VLLM_LLAMA33_70B_URL", "http://localhost:8000/v1")
            ),
        )
        self.drafter_url = getattr(self.drafter, "base_url", drafter_url or "").rstrip("/")
        self.verifier_url = getattr(self.verifier, "base_url", verifier_url or "").rstrip("/")
        self.drafter_model = getattr(self.drafter, "model_id", drafter_model)
        self.verifier_model = getattr(self.verifier, "model_id", verifier_model)
        self.drafter_api_key = getattr(self.drafter, "api_key", "")
        self.verifier_api_key = getattr(self.verifier, "api_key", "")
        self.drafter_temperature = 0.0 if slm_temperature is None else slm_temperature
        self.verifier_temperature = 0.0 if llm_temperature is None else llm_temperature
        self.drafter_max_tokens = max_tokens if slm_max_tokens is None else slm_max_tokens
        self.verifier_max_tokens = max_tokens if llm_max_tokens is None else llm_max_tokens
        self.acceptance_threshold = (
            confidence_threshold if acceptance_threshold is None else acceptance_threshold
        )
        self.task_type = task_type or "open"
        self.verifier_lookahead_tokens = max(int(verifier_lookahead_tokens), 1)
        self._drafter_is_local = _is_local_or_private_endpoint(self.drafter_url)
        self._verifier_is_local = _is_local_or_private_endpoint(self.verifier_url)

    def run(self, query: Query) -> Response:
        prompt = build_prompt(query, self.task_type)
        t0 = time.perf_counter()

        draft = self._generate(
            provider=self.drafter,
            base_url=self.drafter_url,
            api_key=self.drafter_api_key,
            model_name=self.drafter_model,
            messages=_messages(prompt, ""),
            requested_max_tokens=self.drafter_max_tokens,
            temperature=self.drafter_temperature,
        )
        draft_cost = _estimate_cost(
            self.drafter_model,
            prompt_tokens=draft.prompt_tokens,
            completion_tokens=draft.completion_tokens,
            local_endpoint=self._drafter_is_local,
        )

        total_in = draft.prompt_tokens
        total_out = draft.completion_tokens
        total_cost = draft_cost
        draft_text = draft.text
        draft_confidence = _mean_confidence(draft.logprobs)

        accepted_chars = 0
        verifier_requests = 0
        verifier_prompt_tokens = 0
        verifier_completion_tokens = 0
        verification_steps: list[dict[str, object]] = []
        inference_steps: list[dict[str, object]] = [
            {
                "role": "drafter_proposal",
                "model_id": self.drafter_model,
                "latency_ms": draft.latency_ms,
                "input_tokens": draft.prompt_tokens,
                "output_tokens": draft.completion_tokens,
                "api_cost_usd": draft_cost,
            }
        ]
        rewrite_triggered = False
        rewrite_reason = "draft_fully_verified"
        rewrite_suffix: _GenerationResult | None = None
        continuation_fallback_used = False

        while accepted_chars < len(draft_text):
            verifier_window = self._generate(
                provider=self.verifier,
                base_url=self.verifier_url,
                api_key=self.verifier_api_key,
                model_name=self.verifier_model,
                messages=_messages(prompt, draft_text[:accepted_chars]),
                requested_max_tokens=max(
                    1,
                    min(self.verifier_lookahead_tokens, self.verifier_max_tokens or self.verifier_lookahead_tokens),
                ),
                temperature=self.verifier_temperature,
                continue_final_message=accepted_chars > 0,
            )
            continuation_fallback_used = (
                continuation_fallback_used or verifier_window.continuation_fallback_used
            )
            verifier_requests += 1
            verifier_prompt_tokens += verifier_window.prompt_tokens
            verifier_completion_tokens += verifier_window.completion_tokens
            verifier_cost = _estimate_cost(
                self.verifier_model,
                prompt_tokens=verifier_window.prompt_tokens,
                completion_tokens=verifier_window.completion_tokens,
                local_endpoint=self._verifier_is_local,
            )
            total_in += verifier_window.prompt_tokens
            total_out += verifier_window.completion_tokens
            total_cost += verifier_cost

            remaining_draft = draft_text[accepted_chars:]
            match_len = _common_prefix_length(remaining_draft, verifier_window.text)
            accepted_before = accepted_chars
            window_confidence = _mean_confidence(verifier_window.logprobs)
            accepted_chars += match_len

            verification_steps.append(
                {
                    "step": verifier_requests,
                    "accepted_chars_before": accepted_before,
                    "matched_chars": match_len,
                    "accepted_chars_after": accepted_chars,
                    "window_text": verifier_window.text,
                    "remaining_draft_preview": remaining_draft[:160],
                    "window_confidence": window_confidence,
                }
            )
            inference_steps.append(
                {
                    "role": "verifier_check",
                    "model_id": self.verifier_model,
                    "latency_ms": verifier_window.latency_ms,
                    "input_tokens": verifier_window.prompt_tokens,
                    "output_tokens": verifier_window.completion_tokens,
                    "api_cost_usd": verifier_cost,
                }
            )

            if not verifier_window.text:
                rewrite_triggered = True
                rewrite_reason = "empty_verifier_window"
                break
            if window_confidence < self.acceptance_threshold:
                accepted_chars = accepted_before
                rewrite_triggered = True
                rewrite_reason = "verifier_confidence_below_threshold"
                break
            if match_len < len(verifier_window.text):
                rewrite_triggered = True
                rewrite_reason = "verifier_diverged_from_draft"
                break
            if match_len == 0:
                rewrite_triggered = True
                rewrite_reason = "no_verified_progress"
                break

        if rewrite_triggered:
            accepted_prefix = draft_text[:accepted_chars]
            rewrite_suffix = self._generate(
                provider=self.verifier,
                base_url=self.verifier_url,
                api_key=self.verifier_api_key,
                model_name=self.verifier_model,
                messages=_messages(prompt, accepted_prefix),
                requested_max_tokens=self.verifier_max_tokens,
                temperature=self.verifier_temperature,
                continue_final_message=bool(accepted_prefix),
            )
            continuation_fallback_used = (
                continuation_fallback_used or rewrite_suffix.continuation_fallback_used
            )
            verifier_requests += 1
            verifier_prompt_tokens += rewrite_suffix.prompt_tokens
            verifier_completion_tokens += rewrite_suffix.completion_tokens
            rewrite_cost = _estimate_cost(
                self.verifier_model,
                prompt_tokens=rewrite_suffix.prompt_tokens,
                completion_tokens=rewrite_suffix.completion_tokens,
                local_endpoint=self._verifier_is_local,
            )
            total_in += rewrite_suffix.prompt_tokens
            total_out += rewrite_suffix.completion_tokens
            total_cost += rewrite_cost
            inference_steps.append(
                {
                    "role": "verifier_rewrite",
                    "model_id": self.verifier_model,
                    "latency_ms": rewrite_suffix.latency_ms,
                    "input_tokens": rewrite_suffix.prompt_tokens,
                    "output_tokens": rewrite_suffix.completion_tokens,
                    "api_cost_usd": rewrite_cost,
                }
            )
            final_text = accepted_prefix + rewrite_suffix.text
            final_model_id = self.verifier_model
            llm_raw_text = rewrite_suffix.text
            llm_latency_ms = rewrite_suffix.latency_ms
            llm_input_tokens = verifier_prompt_tokens
            llm_output_tokens = verifier_completion_tokens
            llm_cost_usd = total_cost - draft_cost
        else:
            final_text = draft_text
            final_model_id = self.drafter_model
            llm_raw_text = None
            llm_latency_ms = None
            llm_input_tokens = verifier_prompt_tokens
            llm_output_tokens = verifier_completion_tokens
            llm_cost_usd = total_cost - draft_cost

        final_confidence = (
            accepted_chars / len(draft_text)
            if draft_text
            else 1.0
        )
        predicted = parse_answer(final_text, self.task_type)
        latency_ms = (time.perf_counter() - t0) * 1000

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=predicted,
            model_id=final_model_id,
            llm_calls=1 if verifier_requests > 0 else 0,
            latency_ms=latency_ms,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            confidence=final_confidence,
            metadata={
                "prompt_text": prompt,
                "slm_text": draft_text,
                "slm_raw_text": draft_text,
                "slm_model_id": self.drafter_model,
                "slm_input_tokens": draft.prompt_tokens,
                "slm_output_tokens": draft.completion_tokens,
                "slm_cost_usd": draft_cost,
                "slm_latency_ms": draft.latency_ms,
                "slm_confidence": draft_confidence,
                "llm_text": llm_raw_text,
                "llm_raw_text": llm_raw_text,
                "llm_model_id": self.verifier_model,
                "llm_input_tokens": llm_input_tokens,
                "llm_output_tokens": llm_output_tokens,
                "llm_cost_usd": llm_cost_usd,
                "llm_latency_ms": llm_latency_ms,
                "final_text": final_text,
                "final_raw_text": final_text,
                "final_parsed_answer": predicted,
                "final_model_id": final_model_id,
                "final_answer_source": "verifier_rewrite" if rewrite_triggered else "verified_draft",
                "accepted_draft_chars": accepted_chars,
                "accepted_draft_ratio": final_confidence,
                "verification_mode": "incremental_prefix_continuation",
                "continuation_fallback_used": continuation_fallback_used,
                "verifier_requests": verifier_requests,
                "verifier_completion_tokens": verifier_completion_tokens,
                "rewrite_triggered": rewrite_triggered,
                "rewrite_reason": rewrite_reason,
                "accepted_prefix_text": draft_text[:accepted_chars],
                "speculative_acceptance_threshold": self.acceptance_threshold,
                "verifier_lookahead_tokens": self.verifier_lookahead_tokens,
                "verification_steps": verification_steps,
                "used_llm": verifier_requests > 0,
                "escalated": rewrite_triggered,
                "inference_steps": inference_steps,
            },
        )

    def _generate(
        self,
        *,
        provider: ModelProvider,
        base_url: str,
        api_key: str,
        model_name: str,
        messages: list[dict[str, str]],
        requested_max_tokens: int,
        temperature: float,
        continue_final_message: bool = False,
    ) -> _GenerationResult:
        prompt_for_budget = "\n".join(message["content"] for message in messages)
        budget = compute_completion_budget(
            provider,
            prompt_for_budget,
            task_type=self.task_type,
            role="direct",
            requested_max_tokens=requested_max_tokens,
        )
        payload: dict[str, object] = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": budget,
            "logprobs": True,
            "top_logprobs": 1,
        }
        if continue_final_message:
            payload["continue_final_message"] = True
        if _is_qwen35_model(model_name):
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        continuation_prefix = ""
        if continue_final_message and len(messages) >= 2 and messages[-1]["role"] == "assistant":
            continuation_prefix = messages[-1]["content"]

        t0 = time.perf_counter()
        continuation_fallback_used = False
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=120,
        )
        if response.status_code >= 400 and continue_final_message and continuation_prefix:
            continuation_fallback_used = True
            fallback_messages = _continuation_fallback_messages(messages[0]["content"], continuation_prefix)
            fallback_payload: dict[str, object] = {
                "model": model_name,
                "messages": fallback_messages,
                "temperature": temperature,
                "max_tokens": budget,
                "logprobs": True,
                "top_logprobs": 1,
            }
            if _is_qwen35_model(model_name):
                fallback_payload["chat_template_kwargs"] = {"enable_thinking": False}
            response = requests.post(
                f"{base_url}/chat/completions",
                json=fallback_payload,
                headers=headers,
                timeout=120,
            )
        response.raise_for_status()
        latency_ms = (time.perf_counter() - t0) * 1000

        data = response.json()
        choice = data["choices"][0]
        message = choice.get("message", {})
        text = str(message.get("content") or "").strip()
        if continuation_fallback_used and continuation_prefix and text.startswith(continuation_prefix):
            text = text[len(continuation_prefix):].lstrip()
        usage = data.get("usage", {})
        content_logprobs = (choice.get("logprobs") or {}).get("content") or []
        tokens = [
            str(item.get("token", ""))
            for item in content_logprobs
            if isinstance(item, dict)
        ]
        logprobs = [
            float(item["logprob"])
            for item in content_logprobs
            if isinstance(item, dict) and item.get("logprob") is not None
        ]
        return _GenerationResult(
            text=text,
            tokens=tokens,
            logprobs=logprobs,
            prompt_tokens=int(usage.get("prompt_tokens", 0) or 0),
            completion_tokens=int(usage.get("completion_tokens", 0) or 0),
            latency_ms=latency_ms,
            finish_reason=choice.get("finish_reason"),
            continuation_fallback_used=continuation_fallback_used,
        )
