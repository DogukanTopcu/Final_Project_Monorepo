from __future__ import annotations

import asyncio
import json
import re
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
class BlackboardTask:
    id: str
    type: str  # "main_query" | "sub_probe" | "synthesis"
    prompt: str
    status: TaskStatus = TaskStatus.OPEN
    assigned_worker: str | None = None
    dependencies: list[str] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    ttl_expiry: float = 0.0


class DecentralizedBlackboardArchitecture(BaseArchitecture):
    name = "decentralized_blackboard"

    def __init__(
        self,
        slm: ModelProvider,  # Primary Specialist (e.g., Qwen 4B)
        secondary_slm: ModelProvider,  # Complementary Specialist (e.g., Llama 3.2 3B)
        llm: ModelProvider,  # Heavy Sweeper (e.g., Llama 3.3 70B)
        slm_temperature: float = 0.0,
        llm_temperature: float = 0.0,
        slm_max_tokens: int = 0,
        llm_max_tokens: int = 0,
        cost_weight: float = 0.15,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.secondary_slm = secondary_slm
        self.cost_weight = cost_weight
        self.task_type = task_type
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens

        # Metric aggregation across async workers
        self.total_in = 0
        self.total_out = 0
        self.total_cost = 0.0
        self.total_latency = 0.0
        self.llm_calls = 0
        self.inference_steps: list[dict[str, Any]] = []

    def run(self, query: Query) -> Response:
        """
        Synchronous bridge to execute the asynchronous event-driven loop 
        required by the Blackboard architecture.
        """
        self.total_in = self.total_out = 0
        self.total_cost = self.total_latency = 0.0
        self.llm_calls = 0
        self.inference_steps = []

        t0 = time.perf_counter()
        final_answer_text, used_model = asyncio.run(self._orchestrate_blackboard(query))
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
            llm_calls=self.llm_calls,
            metadata={
                "inference_steps": self.inference_steps,
                "framework": "event_driven_pub_sub_swarm",
            },
        )

    async def _orchestrate_blackboard(self, query: Query) -> tuple[str, str]:
        """Core async event loop managing the shared state space."""
        base_prompt = mcq_prompt(query) if self.task_type == "mcq" else open_prompt(query)
        
        blackboard: dict[str, BlackboardTask] = {}
        
        root_id = "task_root"
        blackboard[root_id] = BlackboardTask(
            id=root_id,
            type="main_query",
            prompt=base_prompt,
            # Bumping TTL slightly to 1.5s to ensure local 1-token requests finish
            ttl_expiry=time.time() + 1.5, 
        )

        workers = [
            self._worker_loop("PrimarySLM", self.slm, compute_penalty=0.01, blackboard=blackboard),
            self._worker_loop("SecondarySLM", self.secondary_slm, compute_penalty=0.02, blackboard=blackboard),
            self._heavy_sweeper_loop("HeavySweeper70B", self.llm, compute_penalty=0.50, blackboard=blackboard)
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
        self, name: str, provider: ModelProvider, compute_penalty: float, blackboard: dict[str, BlackboardTask]
    ):
        """Standard SLM consumer loop acting on the shared state matrix."""
        while True:
            for task_id, task in list(blackboard.items()):
                # APPLIED FIX: Strict OPEN check
                if task.status == TaskStatus.OPEN:
                    bid = await self._calculate_bid(provider, task.prompt, compute_penalty)
                    
                    # APPLIED FIX: Double-check state before claiming
                    if bid > 0.65 and task.status == TaskStatus.OPEN:  
                        task.status = TaskStatus.IN_PROGRESS
                        task.assigned_worker = name
                        print(f"[\u2705 {name}] CLAIMED task: {task.id}!")
                        
                        await self._execute_task(name, provider, task, blackboard)
                    else:
                        print(f"[\u26a1 {name}] bid {bid:.2f} on task: {task.id}")
            await asyncio.sleep(0.05)

    async def _heavy_sweeper_loop(
        self, name: str, provider: ModelProvider, compute_penalty: float, blackboard: dict[str, BlackboardTask]
    ):
        """The Lazy Heavyweight loop that intervenes exclusively on timeouts."""
        while True:
            now = time.time()
            for task_id, task in list(blackboard.items()):
                is_sweeping_needed = (
                    task.status == TaskStatus.OPEN
                    and now > task.ttl_expiry
                )

                if is_sweeping_needed:
                    task.status = TaskStatus.IN_PROGRESS
                    task.assigned_worker = name
                    self.llm_calls += 1
                    print(f"[\U0001f6a8 {name}] SWEEPING stale/blocked task: {task.id}")
                    
                    await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.05)

    async def _calculate_bid(self, provider: ModelProvider, prompt: str, compute_penalty: float) -> float:
        """Fast capability self-assessment using raw internal logprobs / fast validation."""
        # RETAINED BASELINE LOGIC: The 1-token raw confidence bid
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

    async def _execute_task(self, worker_name: str, provider: ModelProvider, task: BlackboardTask, blackboard: dict[str, BlackboardTask]):
        """Executes actual model generation, handling fallback creation dynamically."""
        loop = asyncio.get_running_loop()
        
        # APPLIED FIX: Clean reasoning prompt
        execution_prompt = (
            f"Solve the following problem step-by-step.\n"
            f"If you lack the information to solve it, or need a sub-calculation, format a request exactly as: "
            f"SUB_TASK: <query>\n\n"
            f"Problem: {task.prompt}"
        )
        
        budget = compute_completion_budget(provider, execution_prompt, task_type="open", role="swarm_node")

        is_sweeper = "Sweeper" in worker_name
        temperature = self.llm_temperature if is_sweeper else self.slm_temperature

        if is_sweeper:
            budget = self.llm_max_tokens if self.llm_max_tokens > 0 else 2048
        else:
            if self.slm_max_tokens > 0:
                budget = self.slm_max_tokens

        text, conf, in_t, out_t, cost, lat = await loop.run_in_executor(
            None,
            lambda: self._timed_generate(
                provider,
                execution_prompt,
                max_tokens=budget,
                temperature=temperature,
            ),
        )

        self.total_in += in_t
        self.total_out += out_t
        self.total_cost += cost
        self.inference_steps.append({
            "worker": worker_name,
            "model_id": provider.model_id,
            "latency_ms": lat,
            "cost_usd": cost
        })

        # THE FIX: Intercept sub-task generation safely
        if "SUB_TASK:" in text and task.id.count("sub_") < 2:
            # Extract ONLY the first line following the SUB_TASK declaration
            raw_sub = text.split("SUB_TASK:")[1].strip()
            # Stop parsing at the first newline to prevent chained hallucinations
            sub_query = raw_sub.split("\n")[0].strip() 
            
            sub_id = f"sub_{task.id}_{int(time.time() * 1000)}"
            
            blackboard[sub_id] = BlackboardTask(
                id=sub_id,
                type="sub_probe",
                prompt=f"Resolve this localized blocker for the main thread:\n{sub_query}",
                ttl_expiry=time.time() + 0.10 
            )
            task.status = TaskStatus.BLOCKED
            task.dependencies.append(sub_id)
            
            asyncio.create_task(self._await_dependencies_and_resume(worker_name, provider, task, blackboard))
        else:
            task.results["final_output"] = text
            task.status = TaskStatus.RESOLVED

    async def _await_dependencies_and_resume(self, worker_name: str, provider: ModelProvider, task: BlackboardTask, blackboard: dict[str, BlackboardTask]):
        """Non-blocking await loop that patches context once dependencies return clean results."""
        while True:
            if all(blackboard[dep_id].status == TaskStatus.RESOLVED for dep_id in task.dependencies):
                resolved_contexts = [blackboard[dep_id].results["final_output"] for dep_id in task.dependencies]
                
                patched_prompt = (
                    f"{task.prompt}\n\n"
                    f"Resolved parameters gathered from the swarm:\n"
                    f"{chr(10).join(resolved_contexts)}\n"
                    f"Synthesize the final definitive solution."
                )
                
                task.prompt = patched_prompt
                task.status = TaskStatus.OPEN 
                break
            await asyncio.sleep(0.02)