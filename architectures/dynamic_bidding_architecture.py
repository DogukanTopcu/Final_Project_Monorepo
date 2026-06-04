from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import build_prompt, parse_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


class TaskStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


@dataclass
class BiddingTask:
    id: str
    prompt: str
    status: TaskStatus = TaskStatus.OPEN
    assigned_worker: str | None = None
    results: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    ttl_expiry: float = 0.0


class DynamicBiddingArchitecture(BaseArchitecture):
    name = "dynamic_bidding"

    def __init__(
        self,
        slms: list[ModelProvider],  # İstenilen sayıda SLM'i dinamik bir liste olarak alır
        slm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        cost_weight: float = 0.15,
        initial_bid_threshold: float = 0.90,  # İhalenin başlayacağı en yüksek özgüven sınırı
        min_bid_threshold: float = 0.10,      # Süre biterken düşülecek en düşük sınır
        ttl_ms: int = 1500,
        task_type: str = "mcq",
    ) -> None:
        # BaseArchitecture genellikle slm ve llm bekler. LLM kullanmayacağımız için None geçiyoruz.
        super().__init__(slms[0] if slms else None, None)
        self.slms = slms
        self.cost_weight = cost_weight
        self.initial_bid_threshold = initial_bid_threshold
        self.min_bid_threshold = min_bid_threshold
        self.ttl_ms = ttl_ms
        self.task_type = task_type
        self.slm_temperature = slm_temperature
        self.slm_max_tokens = slm_max_tokens

        self.total_in = 0
        self.total_out = 0
        self.total_cost = 0.0
        self.total_latency = 0.0
        self.inference_steps: list[dict[str, Any]] = []

    def run(self, query: Query) -> Response:
        self.total_in = self.total_out = 0
        self.total_cost = self.total_latency = 0.0
        self.inference_steps = []

        t0 = time.perf_counter()
        final_answer_text, used_model, final_confidence = asyncio.run(self._orchestrate_swarm(query))
        self.total_latency = (time.perf_counter() - t0) * 1000

        parsed = parse_answer(final_answer_text, self.task_type)

        return Response(
            query_id=query.id,
            text=final_answer_text,
            predicted_answer=parsed,
            confidence=final_confidence,
            model_id=used_model,
            latency_ms=self.total_latency,
            input_tokens=self.total_in,
            output_tokens=self.total_out,
            cost_usd=self.total_cost,
            llm_calls=0,
            metadata={
                "inference_steps": self.inference_steps,
                "framework": "dynamic_bidding_zero_shot",
            },
        )

    async def _orchestrate_swarm(self, query: Query) -> tuple[str, str, float]:
        base_prompt = build_prompt(query, self.task_type)
        now = time.time()

        blackboard: dict[str, BiddingTask] = {}
        root_id = "task_root"
        blackboard[root_id] = BiddingTask(
            id=root_id,
            prompt=base_prompt,
            created_at=now,
            ttl_expiry=now + (self.ttl_ms / 1000.0),
        )

        # Listeden gelen tüm SLM'ler için dinamik olarak Worker (İşçi) döngüsü oluştur
        workers = []
        for i, slm in enumerate(self.slms):
            penalty = 0.01 * (i + 1)
            workers.append(self._worker_loop(f"Worker_{i+1}_{slm.model_id}", slm, compute_penalty=penalty, blackboard=blackboard))

        async def monitor():
            while True:
                if blackboard[root_id].status == TaskStatus.RESOLVED:
                    break
                # Deadlock koruması: Süre (TTL) bittikten 1 saniye sonra hala alan olmadıysa kır
                if time.time() > blackboard[root_id].ttl_expiry + 1.0:
                    break
                await asyncio.sleep(0.02)

        monitor_task = asyncio.create_task(monitor())
        worker_tasks = [asyncio.create_task(w) for w in workers]

        await monitor_task

        for wt in worker_tasks:
            wt.cancel()

        root_task = blackboard[root_id]
        return root_task.results.get("final_output", ""), root_task.assigned_worker or "unknown", root_task.results.get("confidence", 0.0)

    async def _worker_loop(
        self,
        name: str,
        provider: ModelProvider,
        compute_penalty: float,
        blackboard: dict[str, BiddingTask],
    ) -> None:
        while True:
            for task_id, task in list(blackboard.items()):
                if task.status == TaskStatus.OPEN:
                    bid = await self._calculate_bid(provider, task.prompt, compute_penalty)
                    threshold = self._resolve_threshold(task)
                    
                    # Eğer modelin teklifi, o anki düşen ihalenin (threshold) üzerindeyse görevi kap
                    if bid >= threshold and task.status == TaskStatus.OPEN:
                        task.status = TaskStatus.IN_PROGRESS
                        task.assigned_worker = name
                        await self._execute_task(name, provider, task)
            await asyncio.sleep(0.05)

    def _resolve_threshold(self, task: BiddingTask) -> float:
        """Süre daraldıkça, kabul edilebilir güven skorunu (Threshold) doğrusal olarak düşürür."""
        now = time.time()
        if now >= task.ttl_expiry:
            return self.min_bid_threshold
        
        elapsed = now - task.created_at
        total_ttl = task.ttl_expiry - task.created_at
        decay_ratio = elapsed / total_ttl
        
        # Başlangıç noktasından (0.90) minimum noktasına (0.10) doğru kayma (Decay)
        current_threshold = self.initial_bid_threshold - (decay_ratio * (self.initial_bid_threshold - self.min_bid_threshold))
        return current_threshold

    async def _calculate_bid(
        self,
        provider: ModelProvider,
        prompt: str,
        compute_penalty: float,
    ) -> float:
        loop = asyncio.get_running_loop()
        try:
            # Sadece 1 token üreterek modelin içsel (inherent) güven skorunu ölç
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

    async def _execute_task(
        self,
        worker_name: str,
        provider: ModelProvider,
        task: BiddingTask,
    ) -> None:
        loop = asyncio.get_running_loop()
        
        # SIFIR-ATIM (ZERO-SHOT) PROMPTU: CoT, Reasoning veya Subtask yok. Sadece cevap.
        execution_prompt = (
            "Provide the final answer to the problem below directly. Do not include chain-of-thought or explanation.\n\n"
            f"Problem: {task.prompt}\n"
        )

        budget = compute_completion_budget(provider, execution_prompt, task_type="open", role="swarm_node")
        if self.slm_max_tokens > 0:
            budget = self.slm_max_tokens
        else:
            budget = 128 # CoT olmadığı için uzun bütçeye gerek yok

        text, conf, in_t, out_t, cost, lat = await loop.run_in_executor(
            None,
            lambda: self._timed_generate(
                provider,
                execution_prompt,
                max_tokens=budget,
                temperature=self.slm_temperature,
            ),
        )

        self.total_in += in_t
        self.total_out += out_t
        self.total_cost += cost
        self.inference_steps.append({
            "worker": worker_name,
            "model_id": provider.model_id,
            "latency_ms": lat,
            "cost_usd": cost,
            "bid_won_with_conf": conf
        })

        task.results["final_output"] = text
        task.results["confidence"] = conf
        task.status = TaskStatus.RESOLVED