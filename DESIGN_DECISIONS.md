# Design Decisions
## System, Model, Benchmark, and Measurement Rationale

This document records the current design choices implemented in the repo, not an older aspirational architecture.

## 1. Canonical Semantics

These rules are non-negotiable:
- `HumanEval` means the project's human preference evaluation workflow.
- `custom_stratified` means the custom coding benchmark track.
- `eats` is a metric.
- The experiment product surface is organised into three **modes**:
  - **Monolithic** — `monolithic`. Required as a baseline.
  - **Hybrid** — `routing`, `multi_agent`, and experimental `speculative`.
  - **Ensemble** — `ensemble` and experimental `multi_agent_crew`.
- The frontend renders all six architectures. The original "active surface"
  recommendation for thesis runs remains `routing`, `multi_agent`,
  `ensemble`, plus `monolithic` as a ceiling baseline.
- Ensemble accepts **multiple distinct SLMs**. Each SLM contributes exactly
  one vote; `n_models` is derived from the number of selected SLMs. The
  legacy "one SLM repeated N times" form is still supported but the UI
  defaults to the multi-SLM path.
- Monolithic does not take an SLM at all. The runner skips SLM validation
  and the experiment record stores `slm=None` for monolithic runs.

## 2. Why the System Uses Remote OpenAI-Compatible Endpoints

The project needs reproducible experiments across multiple model tiers without hardwiring the control plane to a single inference backend.

That leads to three decisions:
- use canonical model aliases in `core/model_catalog.py`
- resolve each alias to a remote OpenAI-compatible endpoint
- make the frontend read the same runtime status as the backend and CLI

Practical consequence:
- the local machine acts as the control plane
- the model hosts are external and swappable
- the experiment runner stays provider-agnostic

## 3. Hosting Strategy by Tier

### SLM tier

Chosen deployment:
- one GCP L4 host per small model

Rationale:
- stable
- simple to debug
- enough for `gemma4-4b`, `qwen3.5-4b`, and `llama3.2-3b`

### Mid-tier LLM tier

Chosen deployment:
- one shared GCP G4 / RTX PRO 6000 host

Rationale:
- mid-tier runs do not need multiple hosts at once
- the same public endpoint can be reused while the active model changes
- this keeps experimentation cheaper than provisioning one GPU host per mid-tier model

Operational implication:
- only one mid-tier model should run on that host at a time

### Heavy tier

Chosen deployment:
- one optional Nebius heavy host, ideally H200, otherwise H100 fallback

Rationale:
- heavy models are expensive enough that a shared host is the only practical default
- spot availability is the real bottleneck, not code support

Operational implication:
- heavy-tier experiments are capacity-dependent
- the codebase must remain usable even when the heavy host is unavailable

## 4. Architecture Choices

## Architecture A — `routing`

Flow:
- SLM answers first
- confidence is inspected
- low-confidence cases escalate to the chosen LLM

Why this remains the default first experiment:
- it is the lowest-friction way to compare orchestration against direct LLM reliance
- it exposes a clean tradeoff between accuracy and escalation rate
- it produces the clearest EATS story

## Architecture B — `multi_agent`

Flow:
- proponent response
- opponent critique
- arbitrator final answer

Why it is kept:
- it tests whether structure and disagreement improve output quality
- it is still compatible with the same `Query -> Response` contract

## Architecture C — `ensemble`

Flow:
- multiple SLM passes
- majority or weighted vote
- optional LLM tiebreak

Why it is kept:
- it tests whether redundancy can replace frequent escalation
- it is easier to reason about than legacy speculative experiments

## 5. Status of Monolithic, Speculative, and Multi-Agent Crew

These architectures are no longer "legacy" — they are first-class entries in
the architecture catalog (`GET /api/architectures`) and selectable from the
launch form. Each plays a distinct role:

- `monolithic` is the **required ceiling baseline**: a single LLM with no
  orchestration. Every thesis comparison should include at least one
  monolithic run against the same benchmark.
- `speculative` and `multi_agent_crew` are flagged **experimental** in the
  UI. They are runnable but the thesis narrative should not depend on them.

Routing / multi_agent / ensemble remain the recommended thesis story; the
others provide the ceiling baseline and exploratory comparisons.

## 6. Benchmark Decisions

### Automated benchmarks

The active automated benchmark set is:
- `mmlu`
- `arc`
- `hellaswag`
- `gsm8k`
- `truthfulqa`
- `custom_stratified`

Why this mix:
- it covers MCQ reasoning, commonsense, math, and hallucination resistance
- it keeps the benchmark runner within a single automated pipeline

### HumanEval

HumanEval is intentionally separate.

Why:
- it is a UI-backed preference workflow
- it measures subjective preference, not exact-match correctness
- mixing it into the normal benchmark launcher would blur the evaluation contract

### Custom stratified coding benchmark

Intended meaning:
- easy / medium / hard coding tasks

Current implementation note:
- the codebase still contains a legacy proxy loader until the final coding dataset is dropped in
- this must be replaced before thesis-grade coding conclusions are claimed

## 7. Measurement Decisions

## Response-level fields

The response object now carries:
- latency
- token counts
- API cost
- infra cost
- total cost
- energy estimate
- CO2 estimate
- GPU power estimate

Why:
- raw accuracy alone is not enough for this thesis
- orchestration quality must be judged alongside escalation and resource use

## Host-profile energy estimation

Why estimation is used:
- many experiments run against remote hosts rather than a single local GPU
- direct power counters are not uniformly available from the control plane
- the experiment loop still needs comparable infra and energy numbers

Current policy:
- estimate remote infra cost and energy from model-to-host profiles
- attach the estimate to `metadata["inference_steps"]`
- aggregate it into experiment summaries and MLflow

This is a pragmatic compromise:
- more faithful than reporting zero
- less brittle than pretending all experiments share the same local hardware

## 8. Frontend and Backend Alignment

A major design choice in the current revision is that the frontend no longer invents model/provider state.

Backend responsibilities:
- discover model runtime status from the shared catalog
- validate experiment selections
- reject unrunnable combinations unless `dry_run`

Frontend responsibilities:
- display runnable SLM and LLM aliases
- expose only supported benchmark and architecture combinations
- show which runtime provider and endpoint each selected alias resolves to

Why this matters:
- it prevents launching experiments against stale or imaginary configurations

## 9. Documentation Policy

The docs should reflect the real system, not historical prototypes.

That means:
- no claiming HumanEval is the OpenAI benchmark
- no describing EATS as a benchmark
- no presenting the codebase as AWS-only if the working path is GCP remote serving
- no presenting unsupported architectures as the default experiment flow

## 10. Practical Thesis Baseline

Given the currently validated infrastructure, the most reliable baseline stack is:
- SLMs on GCP L4
- mid-tier LLMs on the shared RTX6000 host
- heavy-tier optional when capacity exists

This is the right compromise between:
- scientific comparability
- deployment cost
- operational simplicity
- time-to-results

## 11. Shared-Host Lock Semantics

The RTX6000 host and the heavy host both serve **one large model at a time**.
That makes them a shared resource the experiment runner must serialize.

The implementation:
- `core/hosts.py` is the static catalog of hosts; each host owns a fixed set
  of canonical aliases.
- `web/backend/services/model_host_service.py` holds a process-wide `Lock`
  per shared host. Any experiment that needs an alias on a shared host
  acquires the lock before running and releases it on exit.
- When the lock is acquired, the service probes `/v1/models` on the host. If
  the currently served model does not match the requested alias, it either
  (a) runs the RTX6000 autoswitch script — when enabled — or (b) raises a
  clear error so the operator can switch the container manually.
- The frontend's `/api/hosts` endpoint surfaces the live lock state and the
  current served alias so users see who is holding the slot before they
  launch.

## 12. Playground & Per-Model Inspection

A `POST /api/playground/chat` endpoint sends a one-shot prompt to a single
model and returns latency, token usage and cost. The frontend `/playground`
page wraps that endpoint and is the recommended way to:

- verify a freshly deployed alias is actually serving correctly
- compare two models' raw outputs on the same prompt
- check that a host switch worked before committing to a long run
