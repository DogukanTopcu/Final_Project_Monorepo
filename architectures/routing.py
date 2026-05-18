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

from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.types import Query, Response
from architectures.base import BaseArchitecture


class RoutingArchitecture(BaseArchitecture):
    name = "routing"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        confidence_threshold: float = 0.7,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.threshold = confidence_threshold
        self.task_type = task_type

    def run(self, query: Query) -> Response:
        prompt = (
            mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        )

        # Step 1: SLM inference
        slm_text, conf, in_tok, out_tok, cost, latency = self._timed_generate(
            self.slm, prompt
        )
        slm_parsed = (
            parse_mcq_answer(slm_text)
            if self.task_type == "mcq"
            else parse_open_answer(slm_text)
        )

        # If the draft answer cannot even be parsed into the expected output
        # format, treat it as low-confidence so routing can escalate.
        if slm_parsed is None:
            conf = min(conf, 0.2)

        total_in = in_tok
        total_out = out_tok
        total_cost = cost
        total_latency = latency
        llm_calls = 0
        final_text = slm_text
        used_model = self.slm.model_id
        llm_text: str | None = None
        llm_input_tokens = 0
        llm_output_tokens = 0
        llm_cost = 0.0
        llm_latency = 0.0

        # Step 2: Escalate if low confidence
        if conf < self.threshold:
            llm_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                self.llm, prompt
            )
            total_in += l_in
            total_out += l_out
            total_cost += l_cost
            total_latency += l_lat
            llm_calls = 1
            final_text = llm_text
            used_model = self.llm.model_id
            llm_input_tokens = l_in
            llm_output_tokens = l_out
            llm_cost = l_cost
            llm_latency = l_lat

        parsed = (
            parse_mcq_answer(final_text)
            if self.task_type == "mcq"
            else parse_open_answer(final_text)
        )

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=parsed,
            confidence=conf,
            model_id=used_model,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": prompt,
                "slm_text": slm_text,
                "slm_confidence": conf,
                "slm_model_id": self.slm.model_id,
                "slm_latency_ms": latency,
                "slm_input_tokens": in_tok,
                "slm_output_tokens": out_tok,
                "slm_cost_usd": cost,
                "escalated": llm_calls == 1,
                "used_llm": llm_calls == 1,
                "confidence_threshold": self.threshold,
                "final_model_id": used_model,
                "llm_text": llm_text,
                "llm_model_id": self.llm.model_id if llm_calls == 1 else None,
                "llm_latency_ms": llm_latency if llm_calls == 1 else None,
                "llm_input_tokens": llm_input_tokens if llm_calls == 1 else None,
                "llm_output_tokens": llm_output_tokens if llm_calls == 1 else None,
                "llm_cost_usd": llm_cost if llm_calls == 1 else None,
            },
        )
