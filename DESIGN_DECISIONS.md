# Design Decisions
## Model Selection, Architecture Rationale, and Benchmark Strategy

> This document records *why* each component was chosen, grounded in the Systematic Literature Review (SLR) findings. Every decision traces back to a specific RQ, SLR study reference, or empirical gap identified in the literature.

---

## 1. Experimental Scope

| Dimension | Choice | Rationale |
|-----------|--------|-----------|
| Domain | General-purpose | Domain-agnostic evaluation isolates architecture effects from domain-specific fine-tuning artifacts |
| Inference mode | Blackbox (string in → string out) | Allows clean comparison across all three architectures without leaking internals |
| System type | Cloud-hosted | No VRAM constraints; enables fair comparison at production-realistic scale |
| SLM parameter ceiling | ≤ 7B | Matches the SLR's own definition of "small language model" (< 7B params, Sections 4.1–4.2) |

---

## 2. Small Language Models (SLM)

All three SLMs are open-weight, ≤ 7B parameters, and publicly available on HuggingFace. The combination was chosen to span three different architectural families and two different parameter scales.

### Selection Table

| Model | Params | Family | Why Selected | SLR Reference |
|-------|--------|--------|-------------|---------------|
| **Phi-3 Mini** | 3.8B | Microsoft | Strongest ≤ 4B general reasoning model in literature; S52 documents human-expert-level performance on conceptual biomedical tasks | S52 (Mehandru et al., BioAgents); Microsoft technical report |
| **Qwen2.5-1.5B** | 1.5B | Alibaba | Used directly in the Proponent-Opponent-Arbitrator architecture (S43); 0.5B version surpassed single-agent LLM baselines — establishes lower-bound efficiency data point | S43 (Erak et al.) |
| **Qwen2.5-7B** | 7B | Alibaba | Same model family as Qwen2.5-1.5B; running both isolates the effect of parameter scale within a controlled family | S43; Qwen2.5 technical report |
| **Llama 3.2 3B** | 3B | Meta | Reference point outside Qwen/Phi families; Llama lineage appears across S3, S9, S59 as the de-facto open-weight reference model | S3, S9, S59 (general Llama references) |

### Why This Combination

Using the same model family at two scales (Qwen2.5-1.5B and 7B) lets us answer: *does parameter count matter once orchestration is held constant?* This directly tests the SLR's Cross-RQ Synthesis claim that *"orchestration, not model size, drives performance."* Phi-3 Mini and Llama 3.2 3B act as cross-family controls.

---

## 3. Large Language Models (LLM — Baseline)

LLMs serve two roles: (1) the monolithic **Setup A baseline**, and (2) the **escalation target** in routing and speculative architectures. All accessed via API — no local inference required for LLMs.

### Selection Table

| Model | Provider | Why Selected | SLR Reference |
|-------|----------|-------------|---------------|
| **GPT-4o** | OpenAI API | Upper-bound accuracy ceiling; most widely cited LLM baseline in SLR | S17 (TeleOracle: 80.80% on domain benchmark) |
| **GPT-4o mini** | OpenAI API | Cost-efficient LLM baseline at same provider; S17 reports 82.05% — outperforming full GPT-4o in that domain | S17 (Alabbasi et al., TeleOracle) |
| **Llama 3 70B** | Together AI / self-hosted | Open-weight LLM; S13 uses a 70B-class model as the cloud component of an edge-cloud hybrid system; enables cost-free LLM baseline when self-hosted on L40S | S13 (Hao et al., Hybrid SLM-LLM for Edge-Cloud) |

### GPT-4o vs GPT-4o mini — Why Both

S17 is the single most directly comparable study in the SLR. It reports both scores on the same benchmark with the same evaluation protocol. Including both means we can calibrate our own accuracy scores against a published external reference — if our GPT-4o mini score is within ~2% of S17's 82.05%, we have evidence our evaluation pipeline is well-calibrated.

---

## 4. Architecture Designs

The three architectures are not alternatives chosen arbitrarily — each one tests a distinct design hypothesis about *where* the intelligence should live in a hybrid system.

### Architecture Overview

| Architecture | Design Hypothesis | LLM Role | Blackbox Compliant |
|-------------|-------------------|----------|-------------------|
| **A — Confidence-Based Routing** | Routing decisions can replace most LLM calls | Optional (fallback only) | Yes |
| **B — Proponent-Opponent-Arbitrator** | Multi-agent debate improves quality beyond single large model | Optional (arbitrator only) | Yes |
| **C — SLM Ensemble + Voting** | Ensemble agreement approximates LLM-level accuracy | Optional (tiebreaker only) | Yes |

### Architecture A — Confidence-Based Query Routing

```
Query → SLM → confidence score
              ├── score ≥ θ  →  SLM answer returned
              └── score < θ  →  LLM answers (escalation)
```

| Attribute | Value |
|-----------|-------|
| Hyperparameter | Confidence threshold θ (default 0.75, tuned via pilot study) |
| LLM call ratio | ~10–30% of queries (depending on θ) |
| Key metric | EATS (Efficiency-Accuracy Trade-off Score) |
| Strength | Simplest implementation; most interpretable trade-off curve |
| Weakness | Confidence calibration quality depends on SLM's log-prob reliability |
| SLR evidence | S49 reports >80% cost reduction; S10 demonstrates instance-level model selection |
| **Primary reference** | S49 (She et al., Token Level Routing), S10 (Alabbasi et al.) |

### Architecture B — Proponent-Opponent-Arbitrator (Multi-Agent)

```
Query → Proponent SLM  →  initial answer
      → Opponent SLM   →  critique
      → Arbitrator (SLM or LLM)  →  synthesized final answer
```

| Attribute | Value |
|-----------|-------|
| Agent count | 3 (proponent, opponent, arbitrator) |
| Models used | Qwen2.5-1.5B (proponent), Qwen2.5-7B (opponent), configurable arbitrator |
| LLM call ratio | 0% if arbitrator=SLM; 1 call/query if arbitrator=LLM |
| Strength | Debate mechanism catches errors that a single SLM would miss |
| Weakness | 3× inference cost vs single-pass; latency is additive |
| SLR evidence | S43 shows 0.5B + 1.5B debate outperforms single-agent GPT-3.5 baseline |
| **Primary reference** | S43 (Erak et al.) |

### Architecture C — SLM Ensemble with Majority Voting

```
Query → SLM instance 1  ─┐
Query → SLM instance 2  ──→  majority vote  →  final answer
Query → SLM instance 3  ─┘       └── tie  →  LLM tiebreaker (optional)
```

| Attribute | Value |
|-----------|-------|
| Ensemble size | 3 (configurable) |
| Voting strategy | Majority vote; weighted vote (by confidence) optional |
| LLM call ratio | ~0–5% (tiebreaker only) |
| Strength | Parallelizable; no sequential dependency; lowest latency of the three |
| Weakness | No correction mechanism — wrong unanimous consensus is fatal |
| SLR evidence | S51 (TextNeX) and S55 (Cielen et al.) show ensemble SLMs competitive with single LLM baselines |
| **Primary reference** | S51, S55 |

### The Central Thesis Connection

The SLR's Cross-RQ Synthesis concludes:
> *"orchestration, not model size, drives performance."*

These three architectures operationalize that claim:
- **A** tests whether routing intelligence (knowing *when* to escalate) beats brute-force LLM use
- **B** tests whether debate-based orchestration beats scale
- **C** tests whether redundancy-based orchestration beats scale

The experimental design is constructed so that all three run on the same benchmarks with the same SLMs, meaning any accuracy difference is attributable solely to orchestration strategy.

---

## 5. Benchmarks

### Standard Benchmarks

| Benchmark | Task type | Split | Samples | Why Included | SLR Reference |
|-----------|-----------|-------|---------|-------------|---------------|
| **MMLU** | Multiple-choice, 57 subjects | test | 1,000 (stratified) | Domain-agnostic breadth; most cited benchmark across SLR | Used as primary metric throughout SLR |
| **GSM8K** | Grade-school math, chain-of-thought | test | 500 | Tests multi-step reasoning; relevant to energy-per-token analysis (longer CoT = more tokens = more cost) | S4 (Wilhelm et al., energy-per-token) |
| **HumanEval (project-specific)** | Human preference evaluation | UI-collected | Target: 100-200 prepared prompts + live user prompts | Measures which architecture users prefer when answers are judged by humans instead of exact-match labels | Supports LLM Arena and live chat evaluation |
| **ARC-Challenge** | Abstract reasoning, adversarially filtered | test | 500 | Routing test: questions intentionally hard for retrieval — forces genuine reasoning vs pattern match | S43, S29 |
| **HellaSwag** | Commonsense completion | validation | 500 | SLMs tend to fail commonsense; reveals where confidence routing correctly escalates | Common SLM evaluation |
| **TruthfulQA** | Hallucination resistance | validation | 500 | Measures whether multi-agent debate (Arch B) reduces hallucination vs single-pass | S33 (uncertainty estimation) |

### HumanEval — Human Preference Evaluation

This project's HumanEval is **not** the OpenAI HumanEval code-generation dataset. It is a UI-backed human evaluation workflow with two surfaces:

| Surface | Prompt Source | Evaluation Method | Output |
|---------|---------------|-------------------|--------|
| **LLM Arena** | Prepared prompt bank | Users compare anonymized model/architecture answers | Pairwise win/tie/lose records |
| **Live Chat Evaluation** | User-written questions | Multiple architectures answer the same user prompt; the user selects the better answer | Real-world preference records |

Recommended safeguards:
- Randomize answer order so users do not know which architecture produced which answer.
- Include **tie** and **skip/unsafe** options so forced choices do not pollute labels.
- Store latency, cost, token count, architecture ID, and model IDs with each answer.
- Use at least 3 independent votes per prepared Arena prompt when possible.
- Keep live-chat votes separate from prepared-prompt votes because prompt distribution differs.

### Custom Benchmark — Stratified Coding Difficulty Set

| Tier | Count | Source | Criteria |
|------|-------|--------|----------|
| Easy | 50 minimum / 100 ideal | Team-authored tasks, MBPP-style beginner problems | Single function, one core concept, direct unit tests |
| Medium | 50 minimum / 100 ideal | MBPP/APPS introductory tasks, rewritten LeetCode-style tasks | Multiple conditions, data structures, edge cases |
| Hard | 50 minimum / 100 ideal | APPS/interview-style tasks, team-authored composites | Multi-step algorithmic reasoning, hidden edge cases |
| **Total** | **150 minimum / 300 ideal** | Curated coding set | Fixed split and versioned JSONL for reproducibility |

**Why this matters:** Standard benchmarks report aggregate accuracy. The stratified coding set reveals *at which programming difficulty level* each architecture diverges. Hypothesis: routing should work well on easy tasks, multi-agent/domain-routing should help on medium and code-specialized tasks, and harder tasks should expose when escalation or verification is necessary.

Recommended record format:

```json
{
  "id": "coding_easy_001",
  "difficulty": "easy",
  "topic": "strings",
  "language": "python",
  "prompt": "Write a function ...",
  "starter_code": "def solve(...):",
  "public_tests": ["assert solve(...) == ..."],
  "hidden_tests": ["assert solve(...) == ..."],
  "scoring_type": "unit_tests",
  "source": "team_authored",
  "constraints": "No external packages."
}
```

---

## 6. Primary Evaluation Metric — EATS

### Gap in Literature

The SLR's RQ2 analysis finds:
> *"cost and energy remain far less reported than accuracy — only 34% of studies include latency and 18% include energy metrics."*

Standard benchmarks (MMLU accuracy, pass@1) only measure *output quality*, not *architectural efficiency*. A system that gets 80% MMLU accuracy by calling GPT-4o on every query is not comparable to one that achieves 78% by routing only 15% of queries to an LLM — yet standard metrics treat them equivalently.

### EATS Formula

```
EATS = Accuracy / (LLM_call_ratio × normalized_cost + ε)

where:
  ε = 0.01  (prevents division by zero for pure-SLM systems)
  normalized_cost = cost_usd / max_cost_in_run  (scales to [0,1])
  LLM_call_ratio = llm_calls / total_queries    (scales to [0,1])
```

### Interpretation

| Scenario | EATS | Interpretation |
|----------|------|----------------|
| Pure SLM, accuracy=0.70 | 70.0 | Extremely efficient; no LLM cost |
| 10% LLM routing, accuracy=0.75 | ~7.4 | Good efficiency-accuracy balance |
| 50% LLM routing, accuracy=0.80 | ~1.6 | Moderate; accuracy gain doesn't justify cost |
| Full LLM (monolithic baseline), accuracy=0.82 | ~0.81 | Lowest EATS; highest accuracy, highest cost |

Higher EATS = better efficiency per unit of accuracy. This metric directly fills the gap identified in the SLR's RQ2.

### Secondary Metrics

| Metric | What it measures | Tool |
|--------|-----------------|------|
| **p50 / p95 latency** | Median and tail response time | Wall-clock timing per query |
| **Energy (kWh)** | Total GPU energy consumed per experiment | CodeCarbon v2.3.4 |
| **CO₂ equivalent (g)** | Carbon footprint of inference | CodeCarbon |
| **Tokens/kWh** | Throughput efficiency | `total_tokens / energy_kwh` |
| **AP/T** | Active Parameters per Token | `model_params / total_tokens` |
| **LLM call ratio** | Fraction of queries escalated | `llm_calls / n_queries` |
| **Cost (USD)** | API cost or compute-equivalent | Token-based pricing |

---

## 7. Fine-Tuning Decision

### Decision Framework

| Factor | Fine-tune | Don't fine-tune |
|--------|-----------|-----------------|
| Research goal | Maximize routing accuracy | Isolate architecture effects |
| Variable control | Adds model-change variable | Keeps model constant across architectures |
| Computational cost | Requires QLoRA run (~4–8 hours) | None |
| Reproducibility | Lower (weights differ from base) | Higher (base models are public) |
| Applicable when | Escalation rate > 40% after pilot study | Escalation rate reasonable (10–30%) |

### Recommendation

**Do not fine-tune by default.** The primary research question is about orchestration strategy, not model optimization. Fine-tuning would confound the architecture comparison.

**Exception trigger:** If the pilot study (100 queries) shows that Architecture A's SLM escalates > 40% of queries to the LLM (indicating poor confidence calibration), apply QLoRA to Phi-3 Mini with an instruction-following dataset to improve calibration. This should be reported as a separate ablation, not the primary experiment.

### If Fine-Tuning Is Needed

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Model | Phi-3 Mini (3.8B) | Best efficiency-accuracy trade-off point for routing calibration |
| Method | QLoRA (4-bit + LoRA r=16) | Cloud-compatible; minimizes VRAM; well-documented |
| Dataset | OpenHermes 2.5 | General instruction-following; improves confidence expression without domain bias |
| Objective | Reduce LLM escalation rate | Target: < 20% escalation on pilot set |
| References | S9 (distillation), S59 (mixed distillation), S17 (fine-tuning + RAG) | |

---

## 8. Decision Summary

```
                    ┌─────────────────────────────────────────┐
                    │         SLR GAP IDENTIFIED               │
                    │  "orchestration > model size"            │
                    │  "cost rarely reported (18%)"            │
                    └──────────────┬──────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ↓                    ↓                    ↓
     ┌────────────────┐  ┌─────────────────┐  ┌────────────────────┐
     │  Architecture  │  │    Benchmark    │  │    Metric (EATS)   │
     │                │  │                 │  │                    │
     │ A: Routing     │  │ MMLU (breadth)  │  │ Accuracy /         │
     │ B: Multi-Agent │  │ GSM8K (math)    │  │ (LLM_ratio × cost) │
     │ C: Ensemble    │  │ HumanEval (UI)  │  │                    │
     │                │  │ Coding (diff.)  │  │ Fills RQ2 gap      │
     └────────────────┘  └─────────────────┘  └────────────────────┘
              │                    │                    │
              └────────────────────┴────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────────┐
                    │         THESIS CONTRIBUTION              │
                    │  First systematic comparison of SLM      │
                    │  orchestration strategies using a        │
                    │  unified efficiency-accuracy metric      │
                    │  (EATS) across 3 architectures,          │
                    │  3 benchmarks, 4 SLMs                    │
                    └─────────────────────────────────────────┘
```

---

## 9. References (SLR Study IDs)

| ID | Citation | Used for |
|----|----------|----------|
| S4 | Wilhelm et al. — energy-per-token analysis | Energy metrics justification |
| S9 | Llama distillation study | Fine-tuning reference |
| S10 | Alabbasi et al. — Customer Reviews instance selection | Architecture A evidence |
| S13 | Hao et al. — Hybrid SLM-LLM Edge-Cloud | Llama 70B LLM baseline justification |
| S17 | Alabbasi et al. — TeleOracle | GPT-4o / GPT-4o mini baseline calibration |
| S29 | Abstract reasoning routing study | ARC benchmark justification |
| S33 | Uncertainty estimation study | TruthfulQA benchmark justification |
| S43 | Erak et al. — Proponent-Opponent-Arbitrator | Architecture B design + Qwen selection |
| S49 | She et al. — Token Level Routing | Architecture A evidence (>80% cost reduction) |
| S51 | TextNeX ensemble study | Architecture C evidence |
| S52 | Mehandru et al. — BioAgents | Phi-3 Mini selection |
| S55 | Cielen et al. — ensemble vs LLM | Architecture C evidence |
| S59 | Mixed distillation study | Fine-tuning reference |
