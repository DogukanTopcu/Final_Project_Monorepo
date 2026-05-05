"""
Architecture B — Proponent-Opponent-Arbitrator (Multi-Agent)
=============================================================
Implements the adversarial debate structure from:
  S43 (Erak et al.): Qwen2.5 0.5B/1.5B POA surpasses vanilla LLM baselines
  S29 (assistant-checker collaboration with memory + feedback loops)

Roles:
  - Proponent  : SLM — generates an initial answer and rationale
  - Opponent   : SLM — critiques the Proponent's reasoning
  - Arbitrator : SLM or LLM (controlled by `arbitrator` param) — given both
                 perspectives, produces the final answer

Paper finding: 1.8× inference-time overhead vs single-model baseline (S43).
LLM is only called if arbitrator="llm", so llm_calls ∈ {0, 1}.
"""
from __future__ import annotations

from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.types import Query, Response
from architectures.base import BaseArchitecture


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
Answer with the letter only (A, B, C or D) for multiple-choice, or a number for math.
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
    ) -> None:
        super().__init__(slm, llm)
        self.arbitrator_role = arbitrator  # "slm" | "llm"
        self.task_type = task_type
        self.n_rounds = n_rounds

    def run(self, query: Query) -> Response:
        base_prompt = (
            mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        )

        total_in = total_out = 0
        total_cost = total_latency = 0.0
        llm_calls = 0

        # --- Proponent (SLM) ---
        prop_prompt = _PROPONENT_TEMPLATE.format(question=base_prompt)
        prop_text, _, in_t, out_t, cost, lat = self._timed_generate(self.slm, prop_prompt)
        total_in += in_t; total_out += out_t
        total_cost += cost; total_latency += lat

        # --- Opponent (SLM) ---
        opp_prompt = _OPPONENT_TEMPLATE.format(proponent_output=prop_text)
        opp_text, _, in_t, out_t, cost, lat = self._timed_generate(self.slm, opp_prompt)
        total_in += in_t; total_out += out_t
        total_cost += cost; total_latency += lat

        # --- Arbitrator (SLM or LLM) ---
        arb_prompt = _ARBITRATOR_TEMPLATE.format(
            question=base_prompt,
            proponent_output=prop_text,
            opponent_output=opp_text,
        )
        if self.arbitrator_role == "llm":
            arb_text, _, in_t, out_t, cost, lat = self._timed_generate(self.llm, arb_prompt)
            llm_calls = 1
        else:
            arb_text, _, in_t, out_t, cost, lat = self._timed_generate(self.slm, arb_prompt)

        total_in += in_t; total_out += out_t
        total_cost += cost; total_latency += lat

        parsed = (
            parse_mcq_answer(arb_text)
            if self.task_type == "mcq"
            else parse_open_answer(arb_text)
        )

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
            },
        )
