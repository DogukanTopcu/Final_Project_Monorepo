from __future__ import annotations

from architectures.blackboard_base import BaseBlackboardArchitecture
from core.models import ModelProvider


class DecentralizedBlackboardArchitecture(BaseBlackboardArchitecture):
    name = "decentralized_blackboard"

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
        allow_nested_subtasks: bool = False,
        max_task_attempts: int = 2,
        max_orchestration_s: float = 120.0,
        claim_policy: str = "highest_bid",
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
            allow_nested_subtasks=allow_nested_subtasks,
            max_task_attempts=max_task_attempts,
            max_orchestration_s=max_orchestration_s,
            claim_policy=claim_policy,
        )

    async def _calculate_bid(
        self,
        worker_name: str,
        provider: ModelProvider,
        prompt: str,
        compute_penalty: float,
    ) -> float:
        try:
            # Cheap confidence probe on a truncated prompt; a single token is
            # enough to read the model's inherent confidence from its logprobs.
            _, raw_conf, _ = await self._probe_confidence(
                worker_name, provider, prompt[:300], max_tokens=1
            )
            return (raw_conf or 0.0) - (self.cost_weight * compute_penalty)
        except Exception:
            return 0.0
