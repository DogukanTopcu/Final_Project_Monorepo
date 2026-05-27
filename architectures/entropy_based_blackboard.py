from __future__ import annotations

import asyncio
import math

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
        bid_threshold: float = 0.65,
        ttl_ms: int = 1500,
        task_type: str = "mcq",
        max_subtasks: int = 2,
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
        )

    async def _calculate_bid(self, provider: ModelProvider, prompt: str, compute_penalty: float) -> float:
        loop = asyncio.get_running_loop()
        try:
            _, avg_prob, _, _, _ = await loop.run_in_executor(
                None,
                lambda: provider.generate(
                    prompt,
                    max_tokens=5,
                    temperature=self.slm_temperature,
                ),
            )
            safe_prob = max(min(avg_prob, 0.999), 0.001)
            entropy = -math.log(safe_prob)
            entropy_penalty_weight = 0.85
            bid = safe_prob - (entropy_penalty_weight * entropy) - (self.cost_weight * compute_penalty)
            return max(bid, 0.0)
        except Exception:
            return 0.0
