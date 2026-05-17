# Project Execution Plan
## CENG415 Senior Design — LLM/SLM Hybrid Architecture Benchmark Platform

> **Goal**: Systematically compare three inference architectures (Monolithic LLM, Multi-Agent SLMs, Hybrid Speculative Decoding) across accuracy, latency, energy, cost, and human preference. HumanEval in this project means UI-backed human evaluation, not the OpenAI HumanEval code-generation dataset.

Selected canonical checkpoints for this iteration:
- Heavy LLM baseline: `llama3.3-70b` → `meta-llama/Llama-3.3-70B-Instruct`
- Small-model pool: `qwen3.5-4b`, `gemma4-4b`, `llama3.2-3b`
- Extended comparison pool: `gpt-oss-120b`, `qwen3.5-27b`, `gpt-oss-20b`, `gemma4-31b`, `gemma4-26b-a4b`, `qwen3.5-35b-a3b`

---

## Work Package Overview

| WP | Title | Duration | Deliverable |
|----|-------|----------|-------------|
| WP1 | Infrastructure Setup | Week 1 | Local vLLM stack + GCP prod model-host matrix verified |
| WP2 | Pilot Study | Week 2 | Calibrated confidence thresholds, stability data |
| WP3 | Full-Scale Experiments | Weeks 3–4 | Raw results JSON for all 3 setups × 3 benchmarks |
| WP4 | Statistical Analysis | Week 5 | ANOVA tables, Pareto plots, energy report |
| WP5 | Documentation & Reporting | Week 6 | Final thesis chapter, reproducibility package |

---

## WP1: Infrastructure Setup

### 1.1 GPU Server Preparation

```bash
# Verify GPU
nvidia-smi --query-gpu=name,memory.total --format=csv

# Install CUDA 12.4+ (recommended for current vLLM builds)
# Install Python 3.11 environment
conda create -n thesis python=3.11 -y && conda activate thesis
pip install -e ".[dev]"
```

**Reference deployment matrix**:
- `g2-standard-24`: `qwen3.5-4b`, `gemma4-4b`, `llama3.2-3b`, `gpt-oss-20b`
- `a2-ultragpu-1g`: `qwen3.5-27b`, `gemma4-31b`, `qwen3.5-35b-a3b`, `gemma4-26b-a4b`
- `a2-ultragpu-2g`: `llama3.3-70b`
- `a2-ultragpu-4g`: `gpt-oss-120b`

Not:
- Küçük ve orta modeller yerelde veya tek GPU host'ta self-host edilebilir.
- En büyük heavy modeller için tek generic GPU host yerine model başına dedicated GCP host yaklaşımı kullanılır.

### 1.2 vLLM Serving Stack

Each model runs as a separate OpenAI-compatible vLLM endpoint. Local development can use `infrastructure/vllm/docker-compose.yml`; GCP/prod uses Terraform-managed dedicated hosts selected via `enabled_vllm_models`.

```bash
# Setup A — Monolithic 70B (local example, port 8000)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.3-70B-Instruct \
  --tensor-parallel-size 4 \
  --max-model-len 32768 \
  --port 8000

# Setup B — small-model pool
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3.5-4B --port 8001
python -m vllm.entrypoints.openai.api_server \
  --model google/gemma-4-E4B-it --port 8002
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.2-3B-Instruct --port 8003

# Setup C uses a 4B drafter (port 8001) + 70B verifier (port 8000)
```

For GCP/prod, the same aliases are routed to private vLLM hosts by setting `THESIS_FORCE_VLLM=1`.

### 1.3 Environment Variables

```bash
# .env (git-ignored)
THESIS_FORCE_VLLM=0
VLLM_LLAMA33_70B_URL=http://localhost:8000/v1
VLLM_QWEN35_4B_URL=http://localhost:8001/v1
VLLM_GEMMA4_E4B_URL=http://localhost:8002/v1
VLLM_LLAMA32_3B_URL=http://localhost:8003/v1
VLLM_QWEN35_27B_URL=http://localhost:8004/v1
VLLM_GPT_OSS_20B_URL=http://localhost:8005/v1
VLLM_GEMMA4_31B_URL=http://localhost:8006/v1
VLLM_QWEN35_35B_A3B_URL=http://localhost:8007/v1
VLLM_GEMMA4_26B_A4B_URL=http://localhost:8008/v1
VLLM_GPT_OSS_120B_URL=http://localhost:8009/v1
MLFLOW_TRACKING_URI=http://localhost:5000
CODECARBON_PROJECT_NAME=thesis_benchmark
```

### 1.4 Verification Checklist

- [ ] `nvidia-smi` shows the target GPU(s) expected by the selected host matrix
- [ ] Required vLLM servers respond to `/v1/models`
- [ ] MLflow UI accessible at port 5000
- [ ] `pytest tests/ -v` → 13 passed
- [ ] CodeCarbon writes to `./emissions.csv`
- [ ] NVML binds to the active GPU devices without error

---

## WP2: Pilot Study (100 Stratified Queries)

**Purpose**: Calibrate the confidence threshold for Setup A (routing) and Setup C (speculative decoding) before committing to the full automated and human-evaluated runs.

### 2.1 Stratified Sample Construction

Draw from the custom stratified coding dataset (`benchmarks/custom_stratified.py`):
- Easy: 10 tasks
- Medium: 10 tasks
- Hard: 10 tasks

Keep the pilot small because every architecture answer may need either unit-test execution or human review.

### 2.2 Threshold Sweep

Test thresholds: **0.70, 0.75, 0.80** for both Setup A and Setup C.

```bash
python experiments/pilot_study.py \
  --n-queries 100 \
  --thresholds 0.70 0.75 0.80 \
  --output pilot_results/
```

### 2.3 Decision Criteria

Select threshold that maximizes EATS score subject to accuracy ≥ 85% of the Llama 3.3 70B baseline on the 100-query pilot.

| Threshold | Expected LLM call ratio | Decision |
|-----------|------------------------|----------|
| 0.70 | ~10–15% | More efficient, less accurate |
| 0.75 | ~20–25% | **Baseline selection** |
| 0.80 | ~35–40% | More accurate, less efficient |

The selected threshold is written to `experiments/configs/arch_a.yaml` and `experiments/configs/arch_c.yaml`.

---

## WP3: Full-Scale Experiments

### 3.1 Benchmark Sizes

| Benchmark | Total available | Sample size | Sampling strategy |
|-----------|----------------|-------------|-------------------|
| MMLU | 14,042 | 1,000 | Stratified by subject |
| GSM8K | 1,319 | 500 | Random |
| HumanEval Arena | Prepared prompt bank | 100-200 prompts | Users compare anonymized answers |
| HumanEval Live Chat | User-generated | Continuous collection | User asks; architectures answer; user picks winner |
| Custom Stratified Coding | Curated set | 150 minimum / 300 ideal | Fixed split across easy, medium, hard |

Automated benchmark inference count depends on selected MMLU/GSM8K/coding sample sizes. HumanEval produces preference records rather than a single exact-match accuracy score.

### 3.1.1 HumanEval UI Design

Two interfaces are required:

| Interface | User Flow | Benchmark Record |
|-----------|-----------|------------------|
| LLM Arena | User sees a prepared question and anonymized answers from multiple architectures, then selects the better answer or tie | `prompt_id`, answer pair, hidden architecture IDs, winner/tie, evaluator/session ID |
| Live Chat | User writes a question; multiple architectures answer; user selects the better response | raw user prompt, answer pair, hidden architecture IDs, winner/tie, optional feedback |

Store answer order after randomization so preference labels can be mapped back to the producing architecture without revealing it to the user.

### 3.1.2 Custom Stratified Coding Dataset

Recommended dataset size:
- Pilot: 30 tasks total, 10 per tier.
- Main thesis set: 150 tasks total, 50 per tier.
- Stronger set if time allows: 300 tasks total, 100 per tier.

Recommended sources:
- Team-authored course-style Python problems.
- MBPP-style beginner programming tasks.
- APPS introductory/interview-style tasks.
- Rewritten LeetCode/HackerRank-style tasks to avoid direct memorization and licensing issues.

Recommended JSONL format:

```json
{
  "id": "coding_medium_042",
  "difficulty": "medium",
  "topic": "arrays",
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

### 3.2 Execution Order

Run each setup independently to avoid GPU memory contention:

```bash
# Setup A — Monolithic 70B
python experiments/run_experiment.py --config experiments/configs/arch_a.yaml

# Setup B — Multi-Agent
python experiments/run_experiment.py --config experiments/configs/arch_b.yaml

# Setup C — Speculative Decoding
python experiments/run_experiment.py --config experiments/configs/arch_c.yaml
```

Or in parallel if the selected host matrix provides enough capacity:
```bash
python experiments/run_experiment.py --architecture all
```

### 3.3 Metrics Collected Per Query

| Metric | Source | Field |
|--------|--------|-------|
| Correct/incorrect | Ground truth comparison | `SampleResult.correct` |
| Latency (ms) | Wall clock | `Response.latency_ms` |
| LLM calls | Architecture counter | `Response.llm_calls` |
| Token count | vLLM response | `Response.input_tokens`, `Response.output_tokens` |
| Energy (kWh) | CodeCarbon + NVML | `Response.energy_kwh` |
| CO2 (g) | CodeCarbon | `Response.co2_g` |
| Cost (USD) | Token pricing | `Response.cost_usd` |

### 3.4 MLflow Experiment Structure

```
mlflow/
  experiments/
    setup_a_mmlu/          run_id, accuracy, eats, p95_latency, energy_kwh
    setup_a_gsm8k/
    setup_a_humaneval_arena/
    setup_b_mmlu/
    ...
    setup_c_humaneval_arena/
```

### 3.5 Fault Tolerance

- Each query result is checkpointed to `results/<exp_id>_checkpoint.jsonl` after completion.
- On restart, completed queries are skipped.
- `ExperimentRunner` accepts `--resume` flag.

---

## WP4: Statistical Analysis

### 4.1 ANOVA + Post-hoc Tests

```bash
python analysis/statistical_analysis.py \
  --results results/ \
  --output analysis/output/
```

**Tests performed** (`evaluation/statistics.py`):
1. **One-way ANOVA** across 3 setups for each metric (accuracy, latency, energy)
2. **Tukey HSD post-hoc** to identify which pairs differ significantly (α = 0.05)
3. **Cohen's d** effect size for each pairwise comparison
4. **Shapiro-Wilk** normality check; if violated, fallback to Kruskal-Wallis

### 4.2 Pareto Frontier Analysis

Plot Accuracy (y-axis) vs Normalized Cost (x-axis) for all setups. Pareto-optimal points are annotated.

```bash
python analysis/pareto_plot.py --results results/ --output figures/
```

### 4.3 Energy & Green AI Report

```bash
python analysis/energy_report.py --results results/ --output reports/energy_report.md
```

Includes:
- Total kWh per setup per benchmark
- Tokens/kWh throughput efficiency
- AP/T (Active Parameters per Token)
- CO2 equivalent (grams)
- Comparison to a single GPT-4o API call baseline

### 4.4 EATS Leaderboard

The EATS score is the primary thesis metric. Rank all setups × benchmarks:

| Setup | Benchmark | Accuracy | LLM Ratio | EATS ↑ |
|-------|-----------|----------|-----------|--------|
| C (Speculative) | MMLU | TBD | TBD | TBD |
| B (Multi-Agent) | MMLU | TBD | TBD | TBD |
| A (Monolithic) | MMLU | TBD | TBD | TBD |

---

## WP5: Documentation

### 5.1 Results Artifacts

```
results/
  setup_a_mmlu_results.json
  setup_b_mmlu_results.json
  setup_c_mmlu_results.json
  ...
reports/
  setup_a_mmlu_report.md
  ...
figures/
  pareto_frontier.png
  accuracy_comparison.png
  energy_per_token.png
  latency_cdf.png
analysis/output/
  anova_results.csv
  tukey_hsd.csv
  cohens_d.csv
  energy_summary.csv
```

### 5.2 Reproducibility Package

```bash
# Create reproducibility snapshot
python scripts/package_results.py --output reproducibility_package.zip
```

Contents: all result JSONs, MLflow export, CodeCarbon emissions.csv, conda environment.yml, git commit hash.

### 5.3 Thesis Chapter Mapping

| Chapter | Relevant code |
|---------|--------------|
| 3. Experimental Setup | `experiments/configs/*.yaml`, `infrastructure/vllm/` |
| 4. Results | `results/*.json`, `reports/*.md` |
| 5. Analysis | `analysis/output/`, `figures/` |
| 6. Discussion | EATS leaderboard, Pareto plot, energy report |

---

## File Checklist

### Core Architecture (Term Report)

- [x] `architectures/routing.py` — confidence-based routing (SLM → LLM)
- [x] `architectures/multi_agent.py` — proponent/opponent/arbitrator
- [x] `architectures/ensemble.py` — majority vote ensemble
- [ ] `architectures/monolithic.py` — **Setup A**: Llama 3.3 70B single-pass via vLLM
- [ ] `architectures/multi_agent_crew.py` — **Setup B**: CrewAI+LangGraph multi-agent
- [ ] `architectures/speculative_decoding.py` — **Setup C**: token-level draft-verify

### Benchmarks

- [x] `benchmarks/mmlu.py`
- [x] `benchmarks/gsm8k.py`
- [x] `benchmarks/hellaswag.py`
- [x] `benchmarks/arc.py`
- [x] `benchmarks/truthfulqa.py`
- [ ] `benchmarks/humaneval.py` — project HumanEval preference records from LLM Arena and live chat
- [ ] `benchmarks/custom_stratified.py` — easy/medium/hard coding problem set

### Evaluation

- [x] `evaluation/metrics.py` — EATS, latency percentiles
- [x] `evaluation/reporter.py` — JSON + Markdown report writer
- [ ] `evaluation/energy.py` — CodeCarbon + NVML GPU power
- [ ] `evaluation/statistics.py` — ANOVA, Tukey HSD, Cohen's d, Pareto
- [ ] `evaluation/cost.py` — AP/T, Tokens/kWh

### Experiments

- [x] `experiments/runner.py` — ExperimentRunner
- [x] `experiments/run_experiment.py` — CLI entry
- [ ] `experiments/pilot_study.py` — 100-query threshold calibration

### Infrastructure

- [x] `infrastructure/terraform/` — GCP VPC/GCE/GCS/Artifact Registry/Secret Manager
- [x] `infrastructure/vllm/docker-compose.yml` — vLLM multi-model serving
- [x] `infrastructure/vllm/serve_model.sh` — launch helper scripts

### Analysis

- [ ] `analysis/statistical_analysis.py` — main analysis runner
- [ ] `analysis/pareto_plot.py` — Pareto frontier visualization
- [ ] `analysis/energy_report.py` — energy/CO2 summary

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Single-host GPU assumptions drift from selected model pool | High | High | Use `enabled_vllm_models` and dedicated prod host matrix; avoid generic one-GPU prod design |
| vLLM version incompatibility | Medium | Medium | Keep docs/runtime on current pinned line (`vllm-openai:v0.19.1`) and validate before deploy |
| HumanEval answer-order or architecture leakage | Medium | High | Randomize answer order and keep architecture labels hidden from evaluators |
| Custom coding benchmark memorization/data leakage | Medium | Medium | Prefer team-authored or rewritten tasks; track source metadata |
| CodeCarbon import failure on headless server | Medium | Low | Wrap in try/except; fall back to NVML only |
| Pilot threshold calibration inconclusive | Low | Medium | Default to 0.75 per literature |

---

## Quick Commands

```bash
# Full test suite
pytest tests/ -v

# Lint
ruff check . && mypy core/ architectures/ evaluation/

# Run pilot study
python experiments/pilot_study.py --n-queries 100 --thresholds 0.70 0.75 0.80

# Run single setup
python experiments/run_experiment.py --config experiments/configs/arch_a.yaml

# Run all setups
python experiments/run_experiment.py --architecture all

# Statistical analysis
python analysis/statistical_analysis.py --results results/

# Start MLflow UI
mlflow ui --port 5000

# Start web UI
cd web/frontend && npm run dev
uvicorn web.backend.main:create_app --factory --port 8080
```
