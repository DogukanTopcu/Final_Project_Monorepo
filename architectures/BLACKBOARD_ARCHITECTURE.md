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

Each worker looks at an OPEN task and computes a **bid** — a quick self-estimate of "how well can I answer this, given my cost?" A worker claims the task only if its bid clears the configured `bid_threshold`. The bid always subtracts a small cost penalty so cheaper workers are slightly preferred:

$$
bid = (\text{quality signal}) - (Cost\_Weight \times Compute\_Penalty)
$$

The **only** thing that separates Blackboard from Entropy Blackboard is the quality signal: Blackboard uses raw confidence; Entropy Blackboard additionally subtracts an uncertainty term read from the model's token distribution. The bid is a real (but tiny) model probe — 1 token for Blackboard, a few tokens for Entropy Blackboard — so its cost and energy are recorded like any other inference step.

3. Sub-tasking

If a worker gets stuck, it emits a strict token: `SUB_TASK: <query>`. The system posts a sub-task, blocks the parent, and resumes once the sub-task resolves.

4. Async execution

Workers run concurrently. The system ends when the root task is RESOLVED. `Response.metadata` records async inference steps.

## 1) Blackboard (Geleneksel Merkezi Olmayan Suru)

Blackboard replaces routing with an async bidding system that bids on **confidence alone**:

$$
bid = Confidence - (Cost\_Weight \times Compute\_Penalty)
$$

- SLMs compute a quick confidence-based bid (the probability on the model's first answer token).
- The first SLM that clears the threshold claims the task.
- If no SLM claims the task before TTL expires, the heavy LLM (sweeper) wakes and solves it.

This is cheap, but blind to the overconfident-but-wrong case: a small model can *sound* certain and still be incorrect, and Blackboard will let it claim the task.

Project role: baseline decentralized swarm with safety fallback.

Implementation: [architectures/blackboard.py](architectures/blackboard.py)

## 2) Entropy-Based Blackboard (Entropi Tabanli Guvenlik Agi)

Entropy Blackboard shares the same board, workers, sweeper, and TTL. It changes **only** the bid, adding an uncertainty penalty on top of confidence:

$$
bid = Confidence - (Entropy\_Weight \times H_{norm}) - (Cost\_Weight \times Compute\_Penalty)
$$

- The probe requests the model's **top-k** next-token distribution (`entropy_top_k`, default 20) instead of just its top pick.
- For the first few output tokens it computes the normalized Shannon entropy $H_{norm} = \dfrac{-\sum_i p_i \ln p_i}{\ln k}$, which lands in $[0, 1]$: ~0 when the model is sharply decided, ~1 when its probability mass is smeared across several options (internally torn).
- `entropy_weight` (default 0.5) scales how hard that uncertainty drags the bid down.

The effect: a model that *sounds* confident but is *internally* undecided gets its bid pulled below the threshold, so the task is handed to the 70B sweeper instead of being answered by a guessing SLM. If a provider cannot return a token distribution (e.g. a hosted API without logprobs), the bid gracefully falls back to confidence-only — identical to plain Blackboard.

Project role: the uncertainty-aware variant — trades a bit more sweeper usage for fewer confident-but-wrong SLM claims.

Implementation: [architectures/entropy_based_blackboard.py](architectures/entropy_based_blackboard.py)

### How they behave differently (what to expect)

| Situation | Blackboard | Entropy Blackboard |
| --- | --- | --- |
| Easy question | An SLM claims it | Same — low entropy, SLM still claims |
| SLM is genuinely sure | SLM claims it | SLM claims it |
| SLM *sounds* sure but is internally torn | SLM claims it (risk of confident-wrong) | Penalty drops the bid → 70B sweeper handles it |
| Hard / ambiguous question | Sometimes an SLM grabs it anyway | More often escalated to the 70B |

Expected trade-off: Entropy Blackboard should be **more accurate / better calibrated** (fewer confident-wrong answers) at the cost of **more 70B calls — slightly slower and pricier**. Setting `entropy_weight` to 0 collapses Entropy Blackboard back into plain Blackboard.

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
- `entropy_weight` (Entropy Blackboard only): how strongly output-distribution uncertainty penalizes the bid. `0` = behaves like plain Blackboard.
- `entropy_top_k` (Entropy Blackboard only): width of the top-k token distribution sampled to estimate entropy.

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