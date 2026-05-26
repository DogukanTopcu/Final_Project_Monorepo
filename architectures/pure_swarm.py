from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from architectures.base import BaseArchitecture
from core.models import ModelProvider
from core.prompt import mcq_prompt, open_prompt, parse_mcq_answer, parse_open_answer
from core.token_budget import compute_completion_budget
from core.types import Query, Response


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"


@dataclass
class SwarmTask:
    id: str
    type: str  # "main_query" | "sub_probe" | "synthesis"
    prompt: str
    status: TaskStatus = TaskStatus.OPEN
    assigned_worker: str | None = None
    dependencies: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    ttl_expiry: float = 0.0


class PureSwarmArchitecture(BaseArchitecture):
    name = "pure_swarm"

    def __init__(
        self,
        slm: ModelProvider,
        secondary_slm: ModelProvider,
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
        cost_weight: float = 0.15,
        bid_threshold: float = 0.65,
        ttl_ms: int = 1500,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, slm)
        self.secondary_slm = secondary_slm
        self.cost_weight = cost_weight
        self.bid_threshold = bid_threshold
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
        final_answer_text, used_model = asyncio.run(self._orchestrate_swarm(query))
        self.total_latency = (time.perf_counter() - t0) * 1000

        parsed = (
            parse_mcq_answer(final_answer_text)
            if self.task_type == "mcq"
            else parse_open_answer(final_answer_text)
        )

        return Response(
            query_id=query.id,
            text=final_answer_text,
            predicted_answer=parsed,
            confidence=0.90,
            model_id=used_model,
            latency_ms=self.total_latency,
            input_tokens=self.total_in,
            output_tokens=self.total_out,
            cost_usd=self.total_cost,
            llm_calls=0,
            metadata={
                "inference_steps": self.inference_steps,
                "framework": "pure_peer_to_peer_swarm",
            },
        )

    async def _orchestrate_swarm(self, query: Query) -> tuple[str, str]:
        base_prompt = mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        now = time.time()

        blackboard: dict[str, SwarmTask] = {}
        root_id = "task_root"
        blackboard[root_id] = SwarmTask(
            id=root_id,
            type="main_query",
            prompt=base_prompt,
            created_at=now,
            ttl_expiry=now + (self.ttl_ms / 1000.0),
        )

        workers = [
            self._worker_loop("SwarmNode_A", self.slm, compute_penalty=0.01, blackboard=blackboard),
            self._worker_loop("SwarmNode_B", self.secondary_slm, compute_penalty=0.01, blackboard=blackboard),
        ]

        async def monitor():
            while True:
                if blackboard[root_id].status == TaskStatus.RESOLVED:
                    break
                await asyncio.sleep(0.02)

        monitor_task = asyncio.create_task(monitor())
        worker_tasks = [asyncio.create_task(w) for w in workers]

        await monitor_task

        for wt in worker_tasks:
            wt.cancel()

        root_task = blackboard[root_id]
        return root_task.results.get("final_output", ""), root_task.assigned_worker or "unknown"

    async def _worker_loop(
        self,
        name: str,
        provider: ModelProvider,
        compute_penalty: float,
        blackboard: dict[str, SwarmTask],
    ) -> None:
        while True:
            for task_id, task in list(blackboard.items()):
                if task.status == TaskStatus.OPEN:
                    bid = await self._calculate_bid(provider, task.prompt, compute_penalty)
                    threshold = self._resolve_threshold(task)
                    if bid >= threshold and task.status == TaskStatus.OPEN:
                        task.status = TaskStatus.IN_PROGRESS
                        task.assigned_worker = name
                        await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.05)

    def _resolve_threshold(self, task: SwarmTask) -> float:
        if time.time() > task.ttl_expiry:
            return 0.0
        return self.bid_threshold

    async def _calculate_bid(
        self,
        provider: ModelProvider,
        prompt: str,
        compute_penalty: float,
    ) -> float:
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

    async def _execute_task(
        self,
        worker_name: str,
        provider: ModelProvider,
        task: SwarmTask,
        blackboard: dict[str, SwarmTask],
    ) -> None:
        loop = asyncio.get_running_loop()
        execution_prompt = (
            "Solve the following problem step-by-step.\n"
            "If you lack the information to solve it, or need a sub-calculation, format a request exactly as: "
            "SUB_TASK: <query>\n\n"
            f"Problem: {task.prompt}"
        )

        budget = compute_completion_budget(provider, execution_prompt, task_type="open", role="swarm_node")
        if self.slm_max_tokens > 0:
            budget = self.slm_max_tokens

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
        })

        if "SUB_TASK:" in text and task.id.count("sub_") < 2:
            raw_sub = text.split("SUB_TASK:")[1].strip()
            sub_query = raw_sub.split("\n")[0].strip()
            sub_id = f"sub_{task.id}_{int(time.time() * 1000)}"
            now = time.time()
            blackboard[sub_id] = SwarmTask(
                id=sub_id,
                type="sub_probe",
                prompt=f"Resolve this localized blocker for the main thread:\n{sub_query}",
                created_at=now,
                ttl_expiry=now + (self.ttl_ms / 1000.0),
            )
            task.status = TaskStatus.BLOCKED
            task.dependencies.append(sub_id)
            asyncio.create_task(self._await_dependencies_and_resume(task, blackboard))
        else:
            task.results["final_output"] = text
            task.status = TaskStatus.RESOLVED

    async def _await_dependencies_and_resume(
        self,
        task: SwarmTask,
        blackboard: dict[str, SwarmTask],
    ) -> None:
        while True:
            if all(blackboard[dep_id].status == TaskStatus.RESOLVED for dep_id in task.dependencies):
                resolved_contexts = [blackboard[dep_id].results["final_output"] for dep_id in task.dependencies]
                task.prompt = (
                    f"{task.prompt}\n\n"
                    "Resolved parameters gathered from the swarm:\n"
                    f"{chr(10).join(resolved_contexts)}\n"
                    "Synthesize the final definitive solution."
                )
                now = time.time()
                task.created_at = now
                task.ttl_expiry = now + (self.ttl_ms / 1000.0)
                task.status = TaskStatus.OPEN
                break
            await asyncio.sleep(0.02)
