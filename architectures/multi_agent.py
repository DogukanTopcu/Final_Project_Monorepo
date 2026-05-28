"""
Architecture B — Proponent-Opponent-Arbitrator (Multi-Agent)
=============================================================
Implements the adversarial debate structure from:
  S43 (Erak et al.): POA-style small-model debate surpasses vanilla LLM baselines
  S29 (assistant-checker collaboration with memory + feedback loops)

Roles:
  - Proponent  : SLM — generates an initial answer and rationale
  - Opponent   : SLM — critiques the Proponent's reasoning
  - Arbitrator : SLM or LLM (controlled by `arbitrator` param) — given both
                 perspectives, produces the final answer

This implementation is configured to run with the selected 2026 model pool
(for example Gemma 4 E4B or Qwen 3.5 4B as the SLM, and any selected non-SLM
checkpoint as the arbitrator).
"""
from __future__ import annotations

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import build_prompt, parse_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response

_PROPONENT_TEMPLATE = """{question}

You are the Proponent. Generate an answer and a concise rationale (2-3 sentences).
Format:
Answer: <letter or number>
Rationale: <your reasoning>"""

_OPPONENT_TEMPLATE = """The Proponent answered:
{proponent_output}

You are the Opponent. Identify any flaws, logical errors, or missing considerations.
Be concise. If the answer is correct, say so and explain why.
Critique:"""

_ARBITRATOR_TEMPLATE = """Question: {question}

Proponent said:
{proponent_output}

Opponent's critique:
{opponent_output}

You are the Arbitrator. Based on both perspectives, give the final definitive answer.
Answer with the option letter only for multiple-choice, or a number for math.
Final Answer:"""


class MultiAgentArchitecture(BaseArchitecture):
    name = "multi_agent"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        arbitrator: str = "slm",
        task_type: str = "mcq",
        n_rounds: int = 1,
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
    ) -> None:
        super().__init__(slm, llm)
        self.arbitrator_role = arbitrator  # "slm" | "llm"
        self.task_type = task_type
        self.n_rounds = n_rounds
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens

    def run(self, query: Query) -> Response:
        base_prompt = build_prompt(query, self.task_type)
        proponent_budget = compute_completion_budget(
            self.slm,
            _PROPONENT_TEMPLATE.format(question=base_prompt),
            task_type=self.task_type,
            role="proponent",
            requested_max_tokens=self.slm_max_tokens,
        )
        opponent_budget = compute_completion_budget(
            self.slm,
            _OPPONENT_TEMPLATE.format(proponent_output=""),
            task_type=self.task_type,
            role="opponent",
            requested_max_tokens=self.slm_max_tokens,
        )

        total_in = total_out = 0
        total_cost = total_latency = 0.0
        llm_calls = 0
        inference_steps: list[dict[str, object]] = []

        # --- Proponent (SLM) ---
        prop_prompt = _PROPONENT_TEMPLATE.format(question=base_prompt)
        prop_text, _, in_t, out_t, cost, lat = self._timed_generate(
            self.slm,
            prop_prompt,
            temperature=self.slm_temperature,
            max_tokens=proponent_budget,
        )
        total_in += in_t
        total_out += out_t
        total_cost += cost
        total_latency += lat
        inference_steps.append(
            {
                "role": "proponent",
                "model_id": self.slm.model_id,
                "latency_ms": lat,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "api_cost_usd": cost,
            }
        )

        # --- Opponent (SLM) ---
        opp_prompt = _OPPONENT_TEMPLATE.format(proponent_output=prop_text)
        opp_text, _, in_t, out_t, cost, lat = self._timed_generate(
            self.slm,
            opp_prompt,
            temperature=self.slm_temperature,
            max_tokens=opponent_budget,
        )
        total_in += in_t
        total_out += out_t
        total_cost += cost
        total_latency += lat
        inference_steps.append(
            {
                "role": "opponent",
                "model_id": self.slm.model_id,
                "latency_ms": lat,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "api_cost_usd": cost,
            }
        )

        # --- Arbitrator (SLM or LLM) ---
        arb_prompt = _ARBITRATOR_TEMPLATE.format(
            question=base_prompt,
            proponent_output=prop_text,
            opponent_output=opp_text,
        )
        arb_budget = compute_completion_budget(
            self.llm if self.arbitrator_role == "llm" else self.slm,
            arb_prompt,
            task_type=self.task_type,
            role="arbitrator",
            requested_max_tokens=self.llm_max_tokens if self.arbitrator_role == "llm" else self.slm_max_tokens,
        )
        if self.arbitrator_role == "llm":
            arb_text, _, in_t, out_t, cost, lat = self._timed_generate(
                self.llm,
                arb_prompt,
                temperature=self.llm_temperature,
                max_tokens=arb_budget,
            )
            llm_calls = 1
        else:
            arb_text, _, in_t, out_t, cost, lat = self._timed_generate(
                self.slm,
                arb_prompt,
                temperature=self.slm_temperature,
                max_tokens=arb_budget,
            )

        total_in += in_t
        total_out += out_t
        total_cost += cost
        total_latency += lat
        inference_steps.append(
            {
                "role": "arbitrator",
                "model_id": self.llm.model_id if llm_calls else self.slm.model_id,
                "latency_ms": lat,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "api_cost_usd": cost,
            }
        )

        parsed = parse_answer(arb_text, self.task_type)

        return Response(
            query_id=query.id,
            text=arb_text,
            predicted_answer=parsed,
            confidence=0.85,
            model_id=self.llm.model_id if llm_calls else self.slm.model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "proponent": prop_text,
                "opponent": opp_text,
                "arbitrator_role": self.arbitrator_role,
                "inference_steps": inference_steps,
            },
        )
