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
        cost_weight: float = 0.15,
        task_type: str = "mcq",
    ) -> None:
        super().__init__(slm, llm)
        self.secondary_slm = secondary_slm
        self.cost_weight = cost_weight
        self.task_type = task_type

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
        # Reset counters for this fresh invocation
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
            confidence=0.90,  # Emergent group confidence
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
        
        # Shared storage matrix (The Blackboard)
        blackboard: dict[str, BlackboardTask] = {}
        
        # Initialize root task
        root_id = "task_root"
        blackboard[root_id] = BlackboardTask(
            id=root_id,
            type="main_query",
            prompt=base_prompt,
            ttl_expiry=time.time() + 0.60, # 600ms grace period before heavy model wakes up
        )

        # Active worker loops monitoring the blackboard
        workers = [
            self._worker_loop("PrimarySLM", self.slm, compute_penalty=0.01, blackboard=blackboard),
            self._worker_loop("SecondarySLM", self.secondary_slm, compute_penalty=0.02, blackboard=blackboard),
            self._heavy_sweeper_loop("HeavySweeper70B", self.llm, compute_penalty=0.50, blackboard=blackboard)
        ]

        # Monitor loop to terminate cleanly once root is completely satisfied
        async def monitor():
            while True:
                if blackboard[root_id].status == TaskStatus.RESOLVED:
                    break
                await asyncio.sleep(0.02)

        # Execute concurrent swarm processing
        monitor_task = asyncio.create_task(monitor())
        worker_tasks = [asyncio.create_task(w) for w in workers]

        await monitor_task

        # Terminate active worker loops cleanly
        for wt in worker_tasks:
            wt.cancel()

        root_task = blackboard[root_id]
        return root_task.results.get("final_output", ""), root_task.assigned_worker or "unknown"

    async def _worker_loop(
        self, name: str, provider: ModelProvider, compute_penalty: float, blackboard: dict[str, BlackboardTask]
    ):
        """Standard SLM consumer loop loop acting on the shared state matrix."""
        while True:
            for task_id, task in list(blackboard.items()):
                if task.status == TaskStatus.OPEN:
                    # Step 1: Decentralized Bidding Verification
                    bid = await self._calculate_bid(provider, task.prompt, compute_penalty)
                    if bid > 0.65:  # Absolute baseline threshold to accept work autonomously
                        task.status = TaskStatus.IN_PROGRESS
                        task.assigned_worker = name
                        
                        # Step 2: Autonomous Execution Mode
                        await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.02)

    async def _heavy_sweeper_loop(
        self, name: str, provider: ModelProvider, compute_penalty: float, blackboard: dict[str, BlackboardTask]
    ):
        """The Lazy Heavyweight loop that intervenes exclusively on timeouts or blocks."""
        while True:
            now = time.time()
            for task_id, task in list(blackboard.items()):
                # Condition: Task is running out of time, or sub-processes are explicitly deadlocked
                is_stale = (task.status == TaskStatus.OPEN and now > task.ttl_expiry)
                is_deadlocked = (task.status == TaskStatus.BLOCKED)

                if is_stale or is_deadlocked:
                    task.status = TaskStatus.IN_PROGRESS
                    task.assigned_worker = name
                    self.llm_calls += 1
                    
                    await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.02)

    async def _calculate_bid(self, provider: ModelProvider, prompt: str, compute_penalty: float) -> float:
        """Fast capability self-assessment using raw internal logprobs / fast validation."""
        # Wrap blocking model execution in executor
        loop = asyncio.get_running_loop()
        try:
            # Micro-evaluation: check confidence score returned by provider for the quick analysis
            _, raw_conf, _, _, _ = await loop.run_in_executor(
                None, lambda: provider.generate(prompt[:300], max_tokens=1)
            )
            return raw_conf - (self.cost_weight * compute_penalty)
        except Exception:
            return 0.0

    async def _execute_task(self, worker_name: str, provider: ModelProvider, task: BlackboardTask, blackboard: dict[str, BlackboardTask]):
        """Executes actual model generation, handling fallback creation dynamically."""
        loop = asyncio.get_running_loop()
        
        # Inject system instructions mapping down the self-subtasking mechanics
        execution_prompt = (
            f"You are operating within a collaborative decentralized swarm. Evaluate your parameters accurately.\n"
            f"If you lack information or are completely stuck, format a sub-query exactly as: "
            f"SUB_TASK: <query>\n\n"
            f"Context: {task.prompt}"
        )
        
        budget = compute_completion_budget(provider, execution_prompt, task_type="open", role="swarm_node")
        
        # Run blocking network inference inside safe thread pool executor
        text, conf, in_t, out_t, cost, lat = await loop.run_in_executor(
            None, lambda: self._timed_generate(provider, execution_prompt, max_tokens=budget)
        )

        # Thread-safe mutation of shared state matrix counters
        self.total_in += in_t
        self.total_out += out_t
        self.total_cost += cost
        self.inference_steps.append({
            "worker": worker_name,
            "model_id": provider.model_id,
            "latency_ms": lat,
            "cost_usd": cost
        })

        # Intercept sub-task generation patterns
        if "SUB_TASK:" in text:
            sub_query = text.split("SUB_TASK:")[1].strip()
            sub_id = f"sub_{task.id}_{int(time.time() * 1000)}"
            
            # Post the payload back onto the board for the Heavy Sweeper or alternative nodes
            blackboard[sub_id] = BlackboardTask(
                id=sub_id,
                type="sub_probe",
                prompt=f"Resolve this localized blocker for the main thread:\n{sub_query}",
                ttl_expiry=time.time() + 0.10 # Immediate low grace period for sub-tasks
            )
            task.status = TaskStatus.BLOCKED
            task.dependencies.append(sub_id)
            
            # Spin up a tracking task to wait for sub-task clearing
            asyncio.create_task(self._await_dependencies_and_resume(worker_name, provider, task, blackboard))
        else:
            # Base termination point reached cleanly
            task.results["final_output"] = text
            task.status = TaskStatus.RESOLVED

    async def _await_dependencies_and_resume(self, worker_name: str, provider: ModelProvider, task: BlackboardTask, blackboard: dict[str, BlackboardTask]):
        """Non-blocking await loop that patches context once dependencies return clean results."""
        while True:
            if all(blackboard[dep_id].status == TaskStatus.RESOLVED for dep_id in task.dependencies):
                # Aggregate downstream data payloads
                resolved_contexts = [blackboard[dep_id].results["final_output"] for dep_id in task.dependencies]
                
                # Reformulate the instruction to clear the execution pathway
                patched_prompt = (
                    f"{task.prompt}\n\n"
                    f"Resolved parameters gathered from the swarm:\n"
                    f"{chr(10).join(resolved_contexts)}\n"
                    f"Synthesize the final definitive solution."
                )
                
                task.prompt = patched_prompt
                task.status = TaskStatus.OPEN  # Re-release back onto the board for final processing run
                break
            await asyncio.sleep(0.02)