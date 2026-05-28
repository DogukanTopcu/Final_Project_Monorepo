from __future__ import annotations

import asyncio

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
        bid_threshold: float = 0.65,
        ttl_ms: int = 1500,
        task_type: str = "mcq",
        max_subtasks: int = 2,
        allow_nested_subtasks: bool = False,
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
        )

    async def _calculate_bid(self, provider: ModelProvider, prompt: str, compute_penalty: float) -> float:
        loop = asyncio.get_running_loop()
        try:
            _, raw_conf, _, _, _ = await loop.run_in_executor(
                None,
                lambda: provider.generate(
                    prompt[:300],
                    max_tokens=1,
                    temperature=self.slm_temperature,
                ),
            )
            return raw_conf - (self.cost_weight * compute_penalty)
        except Exception:
            return 0.0
