"""
Architecture C — SLM Ensemble with Voting
==========================================
Implements parallel SLM inference + voting from:
  S51 (TextNeX): ensemble competing with single LLM baselines
  S55 (Cielen et al.): CPU-only ensembles, majority voting

Design:
  - Multiple SLM instances (same model_id, independent calls) run the same query.
  - Majority voting determines the final answer.
  - LLM is a tiebreaker only when all SLMs disagree (optional, default=off).
  - Weighted voting weights each vote by the SLM's reported confidence.
  - llm_calls = 0 unless tiebreaker triggers.

Note: Runs sequentially in the default implementation. For concurrent execution
the ExperimentRunner uses a ThreadPoolExecutor.
"""
from __future__ import annotations

from collections import Counter

from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.types import Query, Response
from architectures.base import BaseArchitecture


class EnsembleArchitecture(BaseArchitecture):
    name = "ensemble"

    def __init__(
        self,
        slm: ModelProvider,
        llm: ModelProvider,
        n_models: int = 3,
        voting: str = "majority",      # "majority" | "weighted"
        llm_tiebreak: bool = False,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.n_models = n_models
        self.voting = voting
        self.llm_tiebreak = llm_tiebreak
        self.task_type = task_type

    def run(self, query: Query) -> Response:
        prompt = (
            mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        )

        votes: list[str] = []
        confidences: list[float] = []
        total_in = total_out = 0
        total_cost = total_latency = 0.0

        for _ in range(self.n_models):
            text, conf, in_t, out_t, cost, lat = self._timed_generate(self.slm, prompt)
            total_in += in_t; total_out += out_t
            total_cost += cost; total_latency += lat
            parsed = (
                parse_mcq_answer(text)
                if self.task_type == "mcq"
                else parse_open_answer(text)
            )
            if parsed:
                votes.append(parsed)
                confidences.append(conf)

        llm_calls = 0
        final_answer: str | None = None

        if votes:
            if self.voting == "weighted":
                final_answer = self._weighted_vote(votes, confidences)
            else:
                final_answer = self._majority_vote(votes)

        # Tiebreaker: all SLMs disagree (all unique answers)
        if final_answer is None and self.llm_tiebreak:
            llm_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                self.llm, prompt
            )
            total_in += l_in; total_out += l_out
            total_cost += l_cost; total_latency += l_lat
            llm_calls = 1
            final_answer = (
                parse_mcq_answer(llm_text)
                if self.task_type == "mcq"
                else parse_open_answer(llm_text)
            )

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.5

        return Response(
            query_id=query.id,
            text=str(final_answer),
            predicted_answer=final_answer,
            confidence=avg_conf,
            model_id=self.slm.model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "votes": votes,
                "confidences": confidences,
                "voting_method": self.voting,
            },
        )

    @staticmethod
    def _majority_vote(votes: list[str]) -> str | None:
        if not votes:
            return None
        counter = Counter(votes)
        top_answer, top_count = counter.most_common(1)[0]
        # Require strict majority (> half)
        if top_count > len(votes) / 2:
            return top_answer
        return None  # tie → may trigger LLM fallback

    @staticmethod
    def _weighted_vote(votes: list[str], weights: list[float]) -> str | None:
        if not votes:
            return None
        scores: dict[str, float] = {}
        for v, w in zip(votes, weights):
            scores[v] = scores.get(v, 0.0) + w
        if not scores:
            return None
        best = max(scores, key=lambda k: scores[k])
        total = sum(weights)
        if scores[best] / total > 0.5:
            return best
        return None
