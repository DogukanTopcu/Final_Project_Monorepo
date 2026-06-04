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
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from threading import Lock
from time import perf_counter

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import build_prompt, parse_answer
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
        prompt = build_prompt(query, self.task_type)

        votes: list[str] = []
        confidences: list[float] = []
        total_in = total_out = 0
        total_cost = 0.0
        inference_steps: list[dict[str, object]] = []
        member_models: list[str] = []
        member_responses: list[dict[str, object]] = []
        llm_tiebreak_text: str | None = None
        llm_tiebreak_parsed: str | None = None
        llm_generation_metadata: dict[str, object] = {}
        total_latency = 0.0

        provider_counts: dict[int, int] = {}
        for member in self.slms:
            provider_counts[id(member)] = provider_counts.get(id(member), 0) + 1
        provider_locks = {
            provider_id: Lock()
            for provider_id, count in provider_counts.items()
            if count > 1
        }

        def run_member(item: tuple[int, ModelProvider]) -> dict[str, object]:
            idx, member = item
            slm_budget = compute_completion_budget(
                member,
                prompt,
                task_type=self.task_type,
                role="ensemble_member",
                requested_max_tokens=self.slm_max_tokens,
            )
            provider_lock = provider_locks.get(id(member))
            with provider_lock or nullcontext():
                text, conf, in_t, out_t, cost, lat = self._timed_generate(
                    member,
                    prompt,
                    temperature=self.slm_temperature,
                    max_tokens=slm_budget,
                )
                member_generation_metadata = dict(getattr(member, "last_generation_metadata", {}) or {})

            parsed = parse_answer(text, self.task_type)
            return {
                "member_index": idx + 1,
                "role": f"ensemble_member_{idx + 1}",
                "model_id": member.model_id,
                "raw_text": text,
                "parsed_answer": parsed,
                "parse_status": "parsed" if parsed is not None else "unparseable",
                "confidence": conf,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "latency_ms": lat,
                "cost_usd": cost,
                "effective_max_tokens": member_generation_metadata.get("effective_max_tokens"),
                "finish_reason": member_generation_metadata.get("finish_reason"),
            }

        member_phase_started = perf_counter()
        with ThreadPoolExecutor(max_workers=len(self.slms)) as executor:
            member_results = list(executor.map(run_member, enumerate(self.slms)))
        total_latency = (perf_counter() - member_phase_started) * 1000.0

        for member_result in member_results:
            conf = float(member_result["confidence"] or 0.0)
            in_t = int(member_result["input_tokens"])
            out_t = int(member_result["output_tokens"])
            cost = float(member_result["cost_usd"])
            lat = float(member_result["latency_ms"])

            total_in += in_t
            total_out += out_t
            total_cost += cost
            member_models.append(str(member_result["model_id"]))
            member_responses.append(member_result)
            inference_steps.append(
                {
                    "role": member_result["role"],
                    "model_id": member_result["model_id"],
                    "latency_ms": lat,
                    "input_tokens": in_t,
                    "output_tokens": out_t,
                    "api_cost_usd": cost,
                    "effective_max_tokens": member_result["effective_max_tokens"],
                    "finish_reason": member_result["finish_reason"],
                }
            )
            parsed = member_result["parsed_answer"]
            if isinstance(parsed, str):
                votes.append(parsed)
                confidences.append(conf)

        llm_calls = 0
        final_answer: str | None = None
        final_answer_source = "none"
        final_model_id = self.slms[0].model_id

        if votes:
            if self.voting == "weighted":
                final_answer = self._weighted_vote(votes, confidences)
            else:
                final_answer = self._majority_vote(votes)
            if final_answer is not None:
                final_answer_source = "ensemble_vote"

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
            llm_generation_metadata = dict(getattr(self.llm, "last_generation_metadata", {}) or {})
            llm_tiebreak_text = llm_text
            llm_tiebreak_parsed = parse_answer(llm_text, self.task_type)
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
                    "effective_max_tokens": llm_generation_metadata.get("effective_max_tokens"),
                    "finish_reason": llm_generation_metadata.get("finish_reason"),
                }
            )
            final_answer = llm_tiebreak_parsed
            final_answer_source = "llm_tiebreak" if llm_tiebreak_parsed is not None else "none"
            final_model_id = self.llm.model_id

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.5
        vote_counts = Counter(votes)
        member_summary_text = "\n".join(
            f"{member['member_index']}. {member['model_id']}: {member['raw_text']}"
            for member in member_responses
        )
        final_text = str(final_answer) if final_answer is not None else ""

        return Response(
            query_id=query.id,
            text=final_text,
            predicted_answer=final_answer,
            confidence=avg_conf,
            model_id=self.slms[0].model_id,
            latency_ms=total_latency,
            input_tokens=total_in,
            output_tokens=total_out,
            cost_usd=total_cost,
            llm_calls=llm_calls,
            metadata={
                "prompt_text": prompt,
                "slm_text": member_summary_text,
                "final_text": final_text,
                "final_model_id": final_model_id,
                "final_answer_source": final_answer_source,
                "votes": votes,
                "vote_counts": dict(vote_counts),
                "confidences": confidences,
                "voting_method": self.voting,
                "n_models": self.n_models,
                "members": member_models,
                "ensemble_member_responses": member_responses,
                "llm_tiebreak": self.llm_tiebreak,
                "llm_tiebreak_raw_text": llm_tiebreak_text,
                "llm_tiebreak_parsed_answer": llm_tiebreak_parsed,
                "llm_tiebreak_effective_max_tokens": (
                    llm_generation_metadata.get("effective_max_tokens")
                    if llm_tiebreak_text is not None
                    else None
                ),
                "llm_tiebreak_finish_reason": (
                    llm_generation_metadata.get("finish_reason")
                    if llm_tiebreak_text is not None
                    else None
                ),
                "llm_tiebreak_parse_status": (
                    None
                    if llm_tiebreak_text is None
                    else ("parsed" if llm_tiebreak_parsed is not None else "unparseable")
                ),
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
