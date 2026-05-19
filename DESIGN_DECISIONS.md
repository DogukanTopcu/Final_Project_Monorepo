# Design Decisions
## System, Model, Benchmark, and Measurement Rationale

This document records the current design choices implemented in the repo, not an older aspirational architecture.

## 1. Canonical Semantics

These rules are non-negotiable:
- `HumanEval` means the project's human preference evaluation workflow.
- `custom_stratified` means the custom coding benchmark track.
- `eats` is a metric.
- the active experiment product surface supports `routing`, `multi_agent`, and `ensemble`

## 2. Why the System Uses Remote OpenAI-Compatible Endpoints

The project needs reproducible experiments across multiple model tiers without hardwiring the control plane to a single inference backend.

That leads to three decisions:
- use canonical model aliases in `core/model_catalog.py`
- resolve each alias to either Ollama or an OpenAI-compatible endpoint
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

## 5. Why Legacy Monolithic and Speculative Code Is Not the Primary Surface

Some legacy files remain in the repo, but they are not the primary experiment surface anymore.

Reasons:
- the web UI, backend validation, and experiment form are standardized on the shared model catalog
- the thesis control plane now centers on the three active orchestration strategies above
- keeping older prototypes in the repo is acceptable as long as docs and launch surfaces do not present them as the main path

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
