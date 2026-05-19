# Decentralized Blackboard Architecture

An event-driven, bossless SLM swarm with TTL fallback.

This architecture replaces the usual centralized "orchestrator" with a shared memory board. Models are autonomous async workers that watch the board, bid on tasks based on confidence and cost, and only wake the big 70B model when the system stalls.

## Why this is different (and useful for the thesis)

Standard architectures (routing, speculative decoding, debate) assume:

- Synchronous execution: models run in a fixed order.
- Centralized control: a router or arbiter decides who answers.
- Query = single unit of work: prompt in, answer out.

We break all three. Here, tasks are stateful objects on a board (OPEN, IN_PROGRESS, BLOCKED, RESOLVED). The SLMs handle micro-tasks concurrently, and the heavy model is a lazy fallback that only burns tokens when a task truly stalls.

## Core mechanics

1. Blackboard (shared memory)

Queries are posted as `BlackboardTask` objects with a status and a TTL.

2. Autonomous bidding

When a task is OPEN, idle SLMs evaluate it and compute a bid:

$$
Utility = Predicted\_Confidence - (Cost\_Weight \times Compute\_Penalty)
$$

If the utility clears the threshold (e.g., 0.65), the SLM claims the task and flips it to IN_PROGRESS.

3. Sub-tasking (Active Oracle)

If an SLM gets stuck, it emits a strict token: `SUB_TASK: <query>`. The worker loop catches that, marks the main task as BLOCKED, and posts the sub-task to the board. Once the sub-task is resolved, the main task resumes.

4. 70B heavy sweeper

The monolithic model watches the board but avoids fresh tasks due to its high compute penalty. If a task sits unresolved for $>600$ ms or stays BLOCKED, the 70B model wakes up, solves it, and goes back to sleep.

## Integration and setup

1. File placement

Place the implementation as [architectures/blackboard.py](architectures/blackboard.py).

2. Instantiate in the runner

In `ExperimentRunner` or `main.py`, pass two SLMs and one heavy LLM.

```python
from architectures.blackboard import DecentralizedBlackboardArchitecture
from core.models import OpenAICompatibleModel

# Initialize vLLM endpoints
slm_primary = OpenAICompatibleModel(
    model_id="Qwen/Qwen3.5-4B",
    base_url="http://localhost:8001/v1",
)
slm_secondary = OpenAICompatibleModel(
    model_id="meta-llama/Llama-3.2-3B-Instruct",
    base_url="http://localhost:8003/v1",
)
llm_sweeper = OpenAICompatibleModel(
    model_id="meta-llama/Llama-3.3-70B-Instruct",
    base_url="http://localhost:8000/v1",
)

arch = DecentralizedBlackboardArchitecture(
    slm=slm_primary,
    secondary_slm=slm_secondary,
    llm=llm_sweeper,
    cost_weight=0.15,  # Higher => heavier penalty for the 70B model
    task_type="mcq",  # or "open"
)

response = arch.run(query)
print(f"Final Answer: {response.predicted_answer} | Cost: ${response.cost_usd:.5f}")
```

## Hyperparameters to tune

- `cost_weight` (default: 0.15): higher means the swarm avoids the 70B longer.
- `ttl_expiry` (default: 600 ms): lower gives stable latency but higher cost; higher lets SLMs resolve longer chains.
- Bid threshold (default: 0.65, in `_worker_loop`): how confident an SLM must be to claim an OPEN task.

## Expected metadata output

`Response.metadata` contains a flat log of async `inference_steps`. Because execution is non-linear, steps may interleave across models, and latency reflects wall-clock async time rather than a simple sum of per-model generation times.