"""
Architecture C — SLM Ensemble with Voting
==========================================
Implements parallel SLM inference + voting from:
  S51 (TextNeX): ensemble competing with single LLM baselines
  S55 (Cielen et al.): CPU-only ensembles, majority voting

Design:
  - One or more SLM providers run the same query.
  - When a single SLM is supplied, it is invoked `n_models` times (legacy path).
  - When a list of SLM providers is supplied, each provider votes once and
    `n_models` is derived from the list length.
  - Majority voting (default) or weighted-by-confidence voting determines the
    final answer.
  - LLM is a tiebreaker only when no clear majority is reached
    (optional, default=off).
  - llm_calls = 0 unless the tiebreaker triggers.
"""
from __future__ import annotations

from collections import Counter

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


class EnsembleArchitecture(BaseArchitecture):
    name = "ensemble"

    def __init__(
        self,
        slm: ModelProvider | None = None,
        llm: ModelProvider | None = None,
        slms: list[ModelProvider] | None = None,
        n_models: int = 3,
        voting: str = "majority",      # "majority" | "weighted"
        llm_tiebreak: bool = False,
        task_type: str = "mcq",
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
    ) -> None:
        provider_list: list[ModelProvider] = list(slms) if slms else []
        if not provider_list and slm is not None:
            provider_list = [slm] * max(int(n_models), 1)
        if not provider_list:
            raise ValueError("EnsembleArchitecture requires at least one SLM provider.")

        # The first SLM is treated as the canonical for the base class
        # (used by some shared helpers).
        super().__init__(provider_list[0], llm)
        self.slms = provider_list
        self.n_models = len(provider_list)
        self.voting = voting
        self.llm_tiebreak = llm_tiebreak
        self.task_type = task_type
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens

    def run(self, query: Query) -> Response:
        prompt = (
            mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        )

        votes: list[str] = []
        confidences: list[float] = []
        total_in = total_out = 0
        total_cost = total_latency = 0.0
        inference_steps: list[dict[str, object]] = []
        member_models: list[str] = []

        for idx, member in enumerate(self.slms):
            slm_budget = compute_completion_budget(
                member,
                prompt,
                task_type=self.task_type,
                role="ensemble_member",
                requested_max_tokens=self.slm_max_tokens,
            )
            text, conf, in_t, out_t, cost, lat = self._timed_generate(
                member,
                prompt,
                temperature=self.slm_temperature,
                max_tokens=slm_budget,
            )
            total_in += in_t
            total_out += out_t
            total_cost += cost
            total_latency += lat
            member_models.append(member.model_id)
            inference_steps.append(
                {
                    "role": f"ensemble_member_{idx + 1}",
                    "model_id": member.model_id,
                    "latency_ms": lat,
                    "input_tokens": in_t,
                    "output_tokens": out_t,
                    "api_cost_usd": cost,
                }
            )
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

        # Tiebreaker: no clear majority across SLMs
        if final_answer is None and self.llm_tiebreak and self.llm is not None:
            llm_budget = compute_completion_budget(
                self.llm,
                prompt,
                task_type=self.task_type,
                role="llm_tiebreak",
                requested_max_tokens=self.llm_max_tokens,
            )
            llm_text, _, l_in, l_out, l_cost, l_lat = self._timed_generate(
                self.llm,
                prompt,
                temperature=self.llm_temperature,
                max_tokens=llm_budget,
            )
            total_in += l_in
            total_out += l_out
            total_cost += l_cost
            total_latency += l_lat
            llm_calls = 1
            inference_steps.append(
                {
                    "role": "llm_tiebreak",
                    "model_id": self.llm.model_id,
                    "latency_ms": l_lat,
                    "input_tokens": l_in,
                    "output_tokens": l_out,
                    "api_cost_usd": l_cost,
                }
            )
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
            model_id=self.slms[0].model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "votes": votes,
                "confidences": confidences,
                "voting_method": self.voting,
                "n_models": self.n_models,
                "members": member_models,
                "llm_tiebreak": self.llm_tiebreak,
                "inference_steps": inference_steps,
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
