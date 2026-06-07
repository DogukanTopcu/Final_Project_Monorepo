from __future__ import annotations

from architectures.blackboard_base import BaseBlackboardArchitecture
from core.models import ModelProvider


class DecentralizedBlackboardArchitecture(BaseBlackboardArchitecture):
    name = "entropy_blackboard"

    def __init__(
        self,
        slm: ModelProvider,
        secondary_slm: ModelProvider,
        llm: ModelProvider,
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
        cost_weight: float = 0.15,
        bid_threshold: float = 0.8,
        ttl_ms: int = 3500,
        task_type: str = "mcq",
        max_subtasks: int = 2,
        max_task_attempts: int = 2,
        max_orchestration_s: float = 120.0,
        entropy_weight: float = 0.5,
        top_k: int = 20,
    ) -> None:
        super().__init__(
            slm=slm,
            secondary_slm=secondary_slm,
            llm=llm,
            slm_temperature=slm_temperature,
            llm_temperature=llm_temperature,
            slm_max_tokens=slm_max_tokens,
            llm_max_tokens=llm_max_tokens,
            cost_weight=cost_weight,
            bid_threshold=bid_threshold,
            ttl_ms=ttl_ms,
            task_type=task_type,
            max_subtasks=max_subtasks,
            max_task_attempts=max_task_attempts,
            max_orchestration_s=max_orchestration_s,
        )
        self.entropy_weight = entropy_weight
        self.top_k = top_k

    async def _calculate_bid(
        self,
        worker_name: str,
        provider: ModelProvider,
        prompt: str,
        compute_penalty: float,
    ) -> float:
        """Bid penalized by the real Shannon entropy of the output distribution.

        An apparently confident SLM whose token distribution is internally
        uncertain (high H_norm) is pushed below the threshold so the heavy
        sweeper takes the task — the uncertainty-aware claim policy the thesis
        describes. Falls back to the confidence-only proxy when the provider
        does not expose a token distribution (e.g. hosted APIs without logprobs).
        """
        try:
            _, conf, meta = await self._probe_confidence(
                worker_name, provider, prompt, max_tokens=5, top_logprobs=self.top_k
            )
            base = conf or 0.0
            h_norm = meta.get("mean_token_entropy_norm")
            if h_norm is None:
                return base - (self.cost_weight * compute_penalty)
            bid = base - (self.entropy_weight * h_norm) - (self.cost_weight * compute_penalty)
            return max(bid, 0.0)
        except Exception:
            return 0.0
