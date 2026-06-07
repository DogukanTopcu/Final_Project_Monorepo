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
    subtask_spawned: int = 0
    # Bumped whenever a blocked task re-opens (prompt changed) so workers
    # invalidate their cached bid and re-bid against the new prompt.
    version: int = 0
    # Execution attempts, used to cap retries after worker failures.
    attempts: int = 0
    # Workers that errored on this task; they skip it so the sweeper takes over.
    failed_workers: set[str] = field(default_factory=set)


class BaseBlackboardArchitecture(BaseArchitecture):
    name = "blackboard_base"

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
        max_task_attempts: int = 2,
        max_orchestration_s: float = 120.0,
    ) -> None:
        super().__init__(slm, llm)
        self.secondary_slm = secondary_slm
        self.cost_weight = cost_weight
        self.bid_threshold = bid_threshold
        self.ttl_ms = ttl_ms
        self.task_type = task_type
        self.slm_temperature = slm_temperature
        self.llm_temperature = llm_temperature
        self.slm_max_tokens = slm_max_tokens
        self.llm_max_tokens = llm_max_tokens
        self.max_subtasks = max_subtasks
        self.allow_nested_subtasks = allow_nested_subtasks
        self.max_task_attempts = max_task_attempts
        self.max_orchestration_s = max_orchestration_s

        self.total_in = 0
        self.total_out = 0
        self.total_cost = 0.0
        self.total_latency = 0.0
        self.llm_calls = 0
        self.inference_steps: list[dict[str, Any]] = []

    def run(self, query: Query) -> Response:
        self.total_in = self.total_out = 0
        self.total_cost = self.total_latency = 0.0
        self.llm_calls = 0
        self.inference_steps = []

        t0 = time.perf_counter()
        final_answer_text, used_worker, final_confidence, final_model_id = asyncio.run(self._orchestrate_blackboard(query))
        self.total_latency = (time.perf_counter() - t0) * 1000

        parsed = parse_answer(final_answer_text, self.task_type)

        return Response(
            query_id=query.id,
            text=final_answer_text,
            predicted_answer=parsed,
            confidence=final_confidence,
            model_id=used_worker,
            latency_ms=self.total_latency,
            input_tokens=self.total_in,
            output_tokens=self.total_out,
            cost_usd=self.total_cost,
            llm_calls=self.llm_calls,
            metadata={
                "inference_steps": self.inference_steps,
                "framework": "event_driven_pub_sub_swarm",
                # The worker tier that resolved the root task (e.g. PrimarySLM)
                # and the actual model it loaded (e.g. google/gemma-4-E4B-it).
                "final_model_id": final_model_id or used_worker,
                "final_worker": used_worker,
            },
        )

    async def _orchestrate_blackboard(self, query: Query) -> tuple[str, str, float, str | None]:
        base_prompt = build_prompt(query, self.task_type)

        blackboard: dict[str, BlackboardTask] = {}
        root_id = "task_root"
        blackboard[root_id] = BlackboardTask(
            id=root_id,
            type="main_query",
            prompt=base_prompt,
            ttl_expiry=time.time() + (self.ttl_ms / 1000.0),
        )

        workers = [
            self._worker_loop("PrimarySLM", self.slm, compute_penalty=0.01, blackboard=blackboard),
            self._worker_loop("SecondarySLM", self.secondary_slm, compute_penalty=0.02, blackboard=blackboard),
            self._heavy_sweeper_loop("HeavySweeper70B", self.llm, compute_penalty=0.50, blackboard=blackboard),
        ]

        async def monitor():
            deadline = time.time() + self.max_orchestration_s
            while True:
                if blackboard[root_id].status == TaskStatus.RESOLVED:
                    break
                # Belt-and-suspenders deadlock guard: if no worker (not even the
                # sweeper) has resolved the root within the budget, force a
                # best-effort resolution so asyncio.run() can never hang.
                if time.time() > deadline:
                    root = blackboard[root_id]
                    root.results.setdefault("final_output", "")
                    root.results.setdefault("confidence", 0.0)
                    root.assigned_worker = root.assigned_worker or "watchdog_timeout"
                    root.status = TaskStatus.RESOLVED
                    break
                await asyncio.sleep(0.02)

        monitor_task = asyncio.create_task(monitor())
        worker_tasks = [asyncio.create_task(w) for w in workers]

        await monitor_task

        for wt in worker_tasks:
            wt.cancel()

        root_task = blackboard[root_id]
        return (
            root_task.results.get("final_output", ""),
            root_task.assigned_worker or "unknown",
            root_task.results.get("confidence", 0.5),
            root_task.results.get("final_model_id"),
        )

    async def _worker_loop(
        self,
        name: str,
        provider: ModelProvider,
        compute_penalty: float,
        blackboard: dict[str, BlackboardTask],
    ) -> None:
        # Bids are deterministic at temperature 0, so compute each one once per
        # (task, version) and cache it. Re-polling never re-bids — this bounds
        # the bidding inference to ~1 call/worker/task-version instead of one
        # per ~50ms tick. The version invalidates the cache when a blocked task
        # re-opens with a synthesized prompt.
        bids: dict[tuple[str, int], float] = {}
        while True:
            for task_id, task in list(blackboard.items()):
                if task.status != TaskStatus.OPEN or name in task.failed_workers:
                    continue
                key = (task_id, task.version)
                if key not in bids:
                    bids[key] = await self._calculate_bid(
                        name, provider, task.prompt, compute_penalty
                    )
                if bids[key] >= self.bid_threshold and task.status == TaskStatus.OPEN:
                    task.status = TaskStatus.IN_PROGRESS
                    task.assigned_worker = name
                    await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.05)

    async def _heavy_sweeper_loop(
        self,
        name: str,
        provider: ModelProvider,
        compute_penalty: float,
        blackboard: dict[str, BlackboardTask],
    ) -> None:
        while True:
            now = time.time()
            for task_id, task in list(blackboard.items()):
                if task.status == TaskStatus.OPEN and now > task.ttl_expiry:
                    task.status = TaskStatus.IN_PROGRESS
                    task.assigned_worker = name
                    self.llm_calls += 1
                    await self._execute_task(name, provider, task, blackboard)
            await asyncio.sleep(0.05)

    async def _calculate_bid(
        self,
        worker_name: str,
        provider: ModelProvider,
        prompt: str,
        compute_penalty: float,
    ) -> float:
        raise NotImplementedError

    async def _probe_confidence(
        self,
        worker_name: str,
        provider: ModelProvider,
        prompt: str,
        max_tokens: int,
        top_logprobs: int = 1,
    ) -> tuple[str, float | None, dict[str, Any]]:
        """Run a bid probe and account for its real inference cost.

        Bids are genuine ``generate`` calls that consume GPU time. Recording
        them as ``role="bid"`` inference steps (and folding their tokens/cost
        into the run totals) lets evaluation/energy.py attribute their energy and
        CO2, so the swarm's bidding overhead is not invisible in the EATS
        comparison. ``top_logprobs > 1`` opts into the token distribution so the
        entropy variant can read ``mean_token_entropy_norm`` from the returned
        metadata snapshot. Returns ``(text, confidence, metadata)``.
        """
        loop = asyncio.get_running_loop()
        text, conf, in_t, out_t, cost, lat = await loop.run_in_executor(
            None,
            lambda: self._timed_generate(
                provider,
                prompt,
                max_tokens=max_tokens,
                temperature=self.slm_temperature,
                top_logprobs=top_logprobs,
            ),
        )
        # Snapshot the provider's per-call metadata before any later call can
        # overwrite it (a worker serializes calls on its own provider).
        meta = dict(getattr(provider, "last_generation_metadata", {}) or {})
        self.total_in += in_t
        self.total_out += out_t
        self.total_cost += cost
        self.inference_steps.append({
            "worker": worker_name,
            "role": "bid",
            "model_id": provider.model_id,
            "latency_ms": lat,
            "input_tokens": in_t,
            "output_tokens": out_t,
            "api_cost_usd": cost,
            "cost_usd": cost,
        })
        return text, conf, meta

    async def _execute_task(
        self,
        worker_name: str,
        provider: ModelProvider,
        task: BlackboardTask,
        blackboard: dict[str, BlackboardTask],
    ) -> None:
        loop = asyncio.get_running_loop()
        
        depth_limit = self.max_subtasks if self.allow_nested_subtasks else 1
        can_spawn = task.subtask_spawned < self.max_subtasks and task.id.count("sub_") < depth_limit
        if can_spawn:
            execution_prompt = (
                "You are a smart logical reasoning agent acting on a blackboard system.\n"
                "Think briefly about the problem. If you encounter a specific detail or sub-calculation that you are unsure about, DO NOT GUESS.\n"
                "Instead, pause and post a sub-task to the blackboard by writing exactly:\n"
                "SUB_TASK: <your specific query>\n\n"
                "Wait for the blackboard to provide the resolved parameters. Once you receive them, synthesize the final definitive solution.\n"
                "Keep all reasoning extremely brief.\n\n"
                "Example:\n"
                "Problem: Did the author of '1984' also write 'Brave New World'?\n"
                "A. Yes\n"
                "B. No\n"
                "Reasoning: I know '1984' was written by George Orwell. I need to check 'Brave New World'.\n"
                "SUB_TASK: Who wrote the book 'Brave New World'?\n"
                "Resolved parameters gathered from the blackboard:\n"
                "Aldous Huxley.\n"
                "Brief Reasoning (Max 1 sentence): The authors are different.\n"
                "Answer: B\n\n"
                f"Problem:\n{task.prompt.strip()}\n\n"
                "Reasoning:\n"
            )
        else:
            execution_prompt = (
                "You are a smart logical reasoning agent acting on a blackboard system.\n"
                "Think briefly about the problem and provide the final answer.\n"
                "Keep all reasoning extremely brief.\n\n"
                f"Problem:\n{task.prompt.strip()}\n\n"
                "Reasoning:\n"
            )

        budget = compute_completion_budget(provider, execution_prompt, task_type="open", role="swarm_node")
        is_sweeper = "Sweeper" in worker_name
        temperature = self.llm_temperature if is_sweeper else self.slm_temperature

        if is_sweeper:
            budget = self.llm_max_tokens if self.llm_max_tokens > 0 else 2048
        elif self.slm_max_tokens > 0:
            budget = self.slm_max_tokens

        try:
            text, conf, in_t, out_t, cost, lat = await loop.run_in_executor(
                None,
                lambda: self._timed_generate(
                    provider,
                    execution_prompt,
                    max_tokens=budget,
                    temperature=temperature,
                ),
            )
        except Exception as exc:
            # Worker failed (e.g. endpoint blip). Record it, then route the task
            # to the heavy sweeper instead of letting it hang IN_PROGRESS.
            task.failed_workers.add(worker_name)
            task.attempts += 1
            self.inference_steps.append({
                "worker": worker_name,
                "role": "error",
                "model_id": provider.model_id,
                "latency_ms": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "api_cost_usd": 0.0,
                "cost_usd": 0.0,
                "error": str(exc),
            })
            if task.attempts >= self.max_task_attempts:
                # Exhausted retries (even the sweeper failed): resolve
                # best-effort so the orchestrator can never spin forever.
                task.results["final_output"] = ""
                task.results["confidence"] = 0.0
                task.results["final_model_id"] = provider.model_id
                task.status = TaskStatus.RESOLVED
            else:
                # Re-open with an already-expired TTL so the heavy sweeper claims
                # it on its next tick; the failed worker skips it.
                task.ttl_expiry = time.time()
                task.status = TaskStatus.OPEN
            return

        self.total_in += in_t
        self.total_out += out_t
        self.total_cost += cost
        self.inference_steps.append({
            "worker": worker_name,
            "role": "sweep" if is_sweeper else "execution",
            "model_id": provider.model_id,
            "latency_ms": lat,
            "input_tokens": in_t,
            "output_tokens": out_t,
            "api_cost_usd": cost,
            "cost_usd": cost,
        })

        depth_limit = self.max_subtasks if self.allow_nested_subtasks else 1
        if "SUB_TASK:" in text and task.subtask_spawned < self.max_subtasks and task.id.count("sub_") < depth_limit:
            raw_sub = text.split("SUB_TASK:")[1].strip()
            sub_query = raw_sub.split("\n")[0].strip()
            sub_id = f"sub_{task.id}_{int(time.time() * 1000)}"
            task.subtask_spawned += 1
            blackboard[sub_id] = BlackboardTask(
                id=sub_id,
                type="sub_probe",
                prompt=f"Resolve this localized blocker for the main thread:\n{sub_query}",
                ttl_expiry=time.time() + (self.ttl_ms / 1000.0),
            )
            task.status = TaskStatus.BLOCKED
            task.dependencies.append(sub_id)
            asyncio.create_task(self._await_dependencies_and_resume(task, blackboard))
        else:
            task.results["final_output"] = text
            task.results["confidence"] = conf
            task.results["final_model_id"] = provider.model_id
            task.status = TaskStatus.RESOLVED

    async def _await_dependencies_and_resume(
        self,
        task: BlackboardTask,
        blackboard: dict[str, BlackboardTask],
    ) -> None:
        while True:
            if all(blackboard[dep_id].status == TaskStatus.RESOLVED for dep_id in task.dependencies):
                resolved_contexts = [blackboard[dep_id].results["final_output"] for dep_id in task.dependencies]
                task.prompt = (
                    f"{task.prompt}\n\n"
                    "Resolved parameters gathered from the blackboard:\n"
                    f"{chr(10).join(resolved_contexts)}\n"
                    "Synthesize the final definitive solution."
                )
                # New prompt → invalidate cached bids and let every worker
                # (including any that previously failed) re-bid on the synthesis.
                task.version += 1
                task.failed_workers.clear()
                task.status = TaskStatus.OPEN
                task.ttl_expiry = time.time() + (self.ttl_ms / 1000.0)
                break
            await asyncio.sleep(0.02)
