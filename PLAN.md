# Project Execution Plan
## CENG415 Senior Design — Experiment-Ready Track

This plan reflects the current codebase and deployment reality as of `2026-05-19`.

## Objective

Run thesis experiments that compare three orchestration architectures over a shared benchmark, reporting:
- accuracy
- latency
- LLM escalation rate
- API cost
- infra cost
- energy estimate
- CO2 estimate
- EATS

Important terminology:
- `HumanEval` means the project's human preference evaluation workflow
- `custom_stratified` is the coding benchmark track
- `eats` is a metric, not a benchmark

## Current Status Snapshot

Validated runtime pieces:
- local control plane: backend, frontend, MLflow
- GCP L4 SLM hosts:
  - `gemma4-4b`
  - `qwen3.5-4b`
  - `llama3.2-3b`
- GCP G4 / RTX6000 shared mid-tier host:
  - `gpt-oss-20b`
  - `qwen3.5-35b-a3b`
  - remaining RTX-hosted mid-tier aliases can be swapped onto the same host

Blocked or deferred:
- Nebius H200 heavy host may fail due to spot capacity stockouts
- heavy-tier runs should use H200 when available, otherwise H100 fallback is acceptable

## Work Packages

## WP1 — Runtime and Control Plane Stabilization

Deliverables:
- backend reads `.env` correctly
- frontend only exposes launchable architectures and configured models
- experiment service validates alias and runtime availability
- remote endpoint model status is visible in `/models` and the launch form

Exit criteria:
- `GET /models` shows runnable aliases correctly
- one routing run succeeds from the web UI
- one routing run succeeds from the CLI

## WP2 — Automated Benchmark Track

Primary automated benchmarks:
- `mmlu`
- `arc`
- `hellaswag`
- `gsm8k`
- `truthfulqa`
- `custom_stratified`

Target architecture matrix:

| Architecture | Minimum operating scenario |
|---|---|
| `routing` | one SLM + one LLM endpoint |
| `multi_agent` | one SLM alias plus optional LLM arbitrator |
| `ensemble` | one SLM alias plus optional LLM tiebreak |

Minimum benchmark validation:
- 5-sample smoke test for every architecture
- 30 to 100 sample calibration runs before larger comparisons

## WP3 — Mid-Tier and Heavy-Tier Expansion

### Mid-tier shared host

Serve one of these at a time on the RTX6000 host:
- `gpt-oss-20b`
- `qwen3.5-27b`
- `gemma4-31b`
- `qwen3.5-35b-a3b`
- `gemma4-26b-a4b`
- `qwen3.5-122b-a10b`

### Heavy host

Serve one of these at a time on the heavy host:
- `llama3.3-70b`
- `gpt-oss-120b`
- `qwen3.5-397b-a17b`
- `kimi-k2.6-1t`

Operational rule:
- shared hosts run exactly one large model at a time
- `.env` should point aliases to the current public endpoint

## WP4 — Human Preference Evaluation

This is separate from the automated benchmark runner.

Required product surfaces:
- prepared-prompt arena
- live user prompt comparison

Required record fields:
- prompt id or user prompt
- answer A / answer B
- hidden producing architecture ids
- tie / skip support
- latency, token, and cost metadata

Exit criteria:
- HumanEval no longer treated as the OpenAI code benchmark in any user-facing docs
- UI workflow and storage shape are documented before data collection starts

## WP5 — Measurement and Reporting

The result object and reports should contain:
- `accuracy`
- `llm_call_ratio`
- `latency_p50_ms`
- `latency_p95_ms`
- `total_cost_usd`
- `total_api_cost_usd`
- `total_infra_cost_usd`
- `total_energy_kwh`
- `total_co2_g`
- `eats_score`

Measurement policy:
- API-backed models use direct API cost accounting
- self-hosted remote models use host-profile estimates for infra cost and energy
- per-step resource estimates are stored in `Response.metadata["inference_steps"]`

## Recommended Execution Order

1. Keep the local control plane running.
2. Keep all SLM L4 endpoints stable.
3. Use the RTX6000 host for mid-tier sweeps.
4. Only then add heavy-tier experiments if capacity allows.
5. Run automated benchmarks before human preference collection.

## Minimal Experiment Matrix

These are the minimum runs that make the system thesis-usable:

| Benchmark | Architecture | Example pair |
|---|---|---|
| `mmlu` | `routing` | `qwen3.5-4b -> gpt-oss-20b` |
| `mmlu` | `routing` | `llama3.2-3b -> qwen3.5-35b-a3b` |
| `mmlu` | `multi_agent` | `gemma4-4b + qwen3.5-35b-a3b` |
| `mmlu` | `ensemble` | `qwen3.5-4b + gpt-oss-20b` with optional tiebreak |
| `gsm8k` | `routing` | any validated SLM + validated LLM |
| `truthfulqa` | `multi_agent` | any validated SLM + validated LLM |

## Risks and Fallbacks

| Risk | Impact | Fallback |
|---|---|---|
| Nebius H200 spot capacity unavailable | Heavy-tier blocked | Retry later or use H100 |
| Shared host model swap forgotten | Wrong endpoint behind alias | Always verify `/v1/models` before a run |
| HF gated model access missing | Container startup fails | Validate access before serving |
| `custom_stratified` still using proxy data | Coding conclusions weakened | Replace with real coding dataset before final thesis runs |
| HumanEval terminology confusion | Invalid reporting | Keep it clearly separate from OpenAI HumanEval everywhere |

## Exit Criteria for "Experiment-Ready"

The repo is considered experiment-ready when:
- the web UI can launch all three active architectures
- model selection is driven by actual runtime availability
- results include accuracy, latency, cost, energy, CO2, and EATS
- automated benchmark docs and runtime behavior agree
- HumanEval and custom coding benchmark semantics are clearly documented
