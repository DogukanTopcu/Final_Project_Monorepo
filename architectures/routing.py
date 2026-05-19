"""
Architecture A — Confidence-Based Query Routing
================================================
Implements the low-confidence escalation pattern documented in:
  S49 (She et al., Token Level Routing): >80% cost reduction routing <7% tokens
  S10 (Alabbasi et al., Customer Reviews): instance-level model selection

Flow:
  1. SLM answers the query and returns a confidence score.
  2. If confidence ≥ threshold  → return SLM answer (no LLM call).
  3. If confidence < threshold  → escalate full query to LLM.
  4. LLM answer is returned; llm_calls is set to 1.

The confidence threshold is a hyperparameter (default 0.7) tunable via config.
"""
from __future__ import annotations

from typing import Any

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


def should_escalate(
    parsed_answer: str | None,
    confidence: float | None,
    confidence_threshold: float,
    input_tokens: int | None = None,
    top2_margin: float | None = None,
    margin_threshold: float | None = None,
    long_input_token_threshold: int | None = None,
    force_escalate: bool = False,
) -> tuple[bool, str, dict[str, Any]]:
    parse_success = parsed_answer is not None
    input_too_long = bool(
        long_input_token_threshold is not None
        and input_tokens is not None
        and input_tokens > long_input_token_threshold
    )
    low_confidence = confidence is not None and confidence < confidence_threshold
    low_margin = bool(
        margin_threshold is not None
        and top2_margin is not None
        and top2_margin < margin_threshold
    )

    signals = {
        "parse_success": parse_success,
        "confidence": confidence,
        "top2_margin": top2_margin,
        "input_tokens": input_tokens,
        "input_too_long": input_too_long,
        "low_confidence": low_confidence,
        "low_margin": low_margin,
        "forced_escalation": force_escalate,
    }

    if not parse_success:
        return True, "parse_failed", signals
    if confidence is None:
        return True, "missing_confidence", signals
    if low_confidence:
        return True, "confidence_below_threshold", signals
    if low_margin:
        return True, "top2_margin_below_threshold", signals
    if input_too_long:
        return True, "input_too_long", signals
    if force_escalate:
        return True, "forced_escalation", signals
    if margin_threshold is not None and top2_margin is not None:
        return False, "accepted_by_slm_confidence_and_margin", signals
    return False, "accepted_by_slm_confidence", signals


class RoutingArchitecture(BaseArchitecture):
    name = "routing"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        confidence_threshold: float = 0.7,
        task_type: str = "mcq",
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
        slm_only: bool = False,
        margin_threshold: float | None = None,
        long_input_token_threshold: int | None = None,
        force_escalate: bool = False,
        confidence_method: str = "existing_model_confidence",
    ) -> None:
        super().__init__(slm, llm)
        self.threshold = confidence_threshold
        self.task_type = task_type
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens
        self.slm_only = slm_only
        self.margin_threshold = margin_threshold
        self.long_input_token_threshold = long_input_token_threshold
        self.force_escalate = force_escalate
        self.confidence_method = confidence_method

    def _parse_text(self, text: str | None) -> str | None:
        candidate = text or ""
        if self.task_type == "mcq":
            return parse_mcq_answer(candidate)
        return parse_open_answer(candidate)

    def run(self, query: Query) -> Response:
        prompt = (
            mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        )
        slm_budget = compute_completion_budget(
            self.slm,
            prompt,
            task_type=self.task_type,
            role="slm_draft",
            requested_max_tokens=self.slm_max_tokens,
        )

        slm_text, slm_confidence, in_tok, out_tok, cost, latency = self._timed_generate(
            self.slm,
            prompt,
            temperature=self.slm_temperature,
            max_tokens=slm_budget,
        )
        slm_parsed = self._parse_text(slm_text)
        top2_margin = None

        escalate, escalation_reason, signals = should_escalate(
            parsed_answer=slm_parsed,
            confidence=slm_confidence,
            confidence_threshold=self.threshold,
            input_tokens=in_tok,
            top2_margin=top2_margin,
            margin_threshold=self.margin_threshold,
            long_input_token_threshold=self.long_input_token_threshold,
            force_escalate=self.force_escalate,
        )

        total_in = in_tok
        total_out = out_tok
        total_cost = cost
        total_latency = latency
        llm_calls = 0
        final_text = slm_text
        final_parsed = slm_parsed
        final_answer_source = "slm"
        used_model = self.slm.model_id
        llm_text: str | None = None
        llm_parsed: str | None = None
        llm_input_tokens: int | None = None
        llm_output_tokens: int | None = None
        llm_cost: float | None = None
        llm_latency: float | None = None
        inference_steps: list[dict[str, object]] = [
            {
                "role": "slm_draft",
                "model_id": self.slm.model_id,
                "latency_ms": latency,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "api_cost_usd": cost,
            }
        ]

        if escalate and not self.slm_only:
            llm_budget = compute_completion_budget(
                self.llm,
                prompt,
                task_type=self.task_type,
                role="llm_fallback",
                requested_max_tokens=self.llm_max_tokens,
            )
            llm_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                self.llm,
                prompt,
                temperature=self.llm_temperature,
                max_tokens=llm_budget,
            )
            llm_parsed = self._parse_text(llm_text)
            total_in += l_in
            total_out += l_out
            total_cost += l_cost
            total_latency += l_lat
            llm_calls = 1
            final_text = llm_text
            final_parsed = llm_parsed
            used_model = self.llm.model_id
            llm_input_tokens = l_in
            llm_output_tokens = l_out
            llm_cost = l_cost
            llm_latency = l_lat
            if llm_parsed is not None:
                final_answer_source = "llm"
                accepted_by = "llm"
            else:
                final_answer_source = "none"
                accepted_by = "none"
            inference_steps.append(
                {
                    "role": "llm_fallback",
                    "model_id": self.llm.model_id,
                    "latency_ms": l_lat,
                    "input_tokens": l_in,
                    "output_tokens": l_out,
                    "api_cost_usd": l_cost,
                }
            )
        else:
            accepted_by = "slm"
            if escalate and self.slm_only:
                final_answer_source = "slm" if final_parsed is not None else "none"

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=final_parsed,
            confidence=slm_confidence,
            model_id=used_model,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": prompt,
                "slm_text": slm_text,
                "final_text": final_text,
                "slm_raw_text": slm_text,
                "slm_parsed_answer": slm_parsed,
                "slm_parse_status": "parsed" if slm_parsed is not None else "unparseable",
                "slm_confidence": slm_confidence,
                "slm_model_id": self.slm.model_id,
                "slm_latency_ms": latency,
                "slm_input_tokens": in_tok,
                "slm_output_tokens": out_tok,
                "slm_cost_usd": cost,
                "llm_text": llm_text,
                "llm_raw_text": llm_text,
                "llm_parsed_answer": llm_parsed,
                "llm_parse_status": (
                    None
                    if llm_text is None
                    else ("parsed" if llm_parsed is not None else "unparseable")
                ),
                "llm_model_id": self.llm.model_id if llm_calls == 1 else None,
                "llm_latency_ms": llm_latency,
                "llm_input_tokens": llm_input_tokens,
                "llm_output_tokens": llm_output_tokens,
                "llm_cost_usd": llm_cost,
                "escalated": llm_calls == 1,
                "used_llm": llm_calls == 1,
                "slm_only": self.slm_only,
                "confidence_threshold": self.threshold,
                "margin_threshold": self.margin_threshold,
                "long_input_token_threshold": self.long_input_token_threshold,
                "force_escalate": self.force_escalate,
                "confidence_method": self.confidence_method,
                "top2_margin": top2_margin,
                "final_model_id": used_model,
                "final_raw_text": final_text,
                "final_parsed_answer": final_parsed,
                "final_answer_source": final_answer_source,
                "escalation_reason": escalation_reason,
                "routing_decision": {
                    "accepted_by": accepted_by,
                    "threshold": self.threshold,
                    "confidence_method": self.confidence_method,
                    "escalation_requested": escalate,
                    "slm_only_mode": self.slm_only,
                    "signals": signals,
                },
                "inference_steps": inference_steps,
            },
        )
