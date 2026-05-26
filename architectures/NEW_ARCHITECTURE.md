# Swarm Architecture Variants

This document describes three related swarm architectures used in the thesis:

- Blackboard: decentralized swarm with heavy LLM fallback.
- Entropy Blackboard: same as Blackboard, but bidding uses entropy.
- Pure Swarm: fully SLM-only, no heavy fallback.

All three share the same core idea: remove centralized routing and let autonomous workers claim tasks from a shared board.

## Common mechanics

1. Shared board (blackboard)

Queries and sub-queries are posted as tasks with a status (OPEN, IN_PROGRESS, BLOCKED, RESOLVED) and a TTL. Workers continuously scan the board and react to OPEN tasks.

2. Bidding

Workers compute a bid and claim a task if the bid exceeds the configured threshold:

$$
Utility = Predicted\_Confidence - (Cost\_Weight \times Compute\_Penalty)
$$

3. Sub-tasking

If a worker gets stuck, it emits a strict token: `SUB_TASK: <query>`. The system posts a sub-task, blocks the parent, and resumes once the sub-task resolves.

4. Async execution

Workers run concurrently. The system ends when the root task is RESOLVED. `Response.metadata` records async inference steps.

## 1) Blackboard (Geleneksel Merkezi Olmayan Suru)

Blackboard replaces routing with an async bidding system:

- SLMs compute a quick confidence-based bid.
- The first SLM that clears the threshold claims the task.
- If no SLM claims the task before TTL expires, the heavy LLM (sweeper) wakes and solves it.

Project role: baseline decentralized swarm with safety fallback.

Implementation: [architectures/blackboard.py](architectures/blackboard.py)

## 2) Entropy-Based Blackboard (Entropi Tabanli Guvenlik Agi)

Entropy Blackboard shares the same flow as Blackboard, but changes the bidding calculation:

- The model produces token probabilities (logprobs).
- Shannon entropy is computed from the distribution.
- High entropy indicates uncertainty, so the bid is penalized.

Advantage: reduces hallucinations by preventing overconfident claims from uncertain SLMs, sending hard cases to the sweeper earlier.

Project role: improves routing quality using objective information-theoretic signals.

Implementation: [architectures/entropy_based_blackboard.py](architectures/entropy_based_blackboard.py)

## 3) Pure Swarm (Saf Suru Zekasi - Tam Otonomi)

Pure Swarm removes the heavy LLM entirely:

- All SLMs are peers; no hierarchy.
- There is no sweeper fallback.
- To avoid deadlock, the bid threshold decays after TTL (it drops to 0).

Project role: shows how far a pure SLM-only swarm can go on constrained hardware.

Implementation: [architectures/pure_swarm.py](architectures/pure_swarm.py)

## Key parameters (shared)

- `cost_weight`: penalizes expensive workers in the bid.
- `bid_threshold`: minimum bid required to claim an OPEN task.
- `ttl_ms`: TTL for tasks; after this, Blackboard variants allow the sweeper to claim, and Pure Swarm drops the threshold to 0.

## Example usage

```python
from architectures.blackboard import DecentralizedBlackboardArchitecture
from core.models import OpenAICompatibleModel

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
    cost_weight=0.15,
    bid_threshold=0.65,
    ttl_ms=1500,
    task_type="mcq",
)

response = arch.run(query)
print(f"Final Answer: {response.predicted_answer} | Cost: ${response.cost_usd:.5f}")
```

## Thesis narrative summary

We first enabled agent coordination using Blackboard. We then improved decision quality with Entropy Blackboard. Finally, Pure Swarm answers the question: can small agents solve tasks without a 70B safety net?