# Project Execution Plan
## CENG415 Senior Design — LLM/SLM Hybrid Architecture Benchmark Platform

> **Goal**: Systematically compare three inference architectures (Monolithic LLM, Multi-Agent SLMs, Hybrid Speculative Decoding) across accuracy, latency, energy, and cost on MMLU, GSM8K, and HumanEval benchmarks.

---

## Work Package Overview

| WP | Title | Duration | Deliverable |
|----|-------|----------|-------------|
| WP1 | Infrastructure Setup | Week 1 | vLLM serving stack on L40S, environment verified |
| WP2 | Pilot Study | Week 2 | Calibrated confidence thresholds, stability data |
| WP3 | Full-Scale Experiments | Weeks 3–4 | Raw results JSON for all 3 setups × 3 benchmarks |
| WP4 | Statistical Analysis | Week 5 | ANOVA tables, Pareto plots, energy report |
| WP5 | Documentation & Reporting | Week 6 | Final thesis chapter, reproducibility package |

---

## WP1: Infrastructure Setup

### 1.1 GPU Server Preparation (L40S 48GB)

```bash
# Verify GPU
nvidia-smi --query-gpu=name,memory.total --format=csv

# Install CUDA 12.1+ (required by vLLM 0.4.x)
# Install Python 3.11 environment
conda create -n thesis python=3.11 -y && conda activate thesis
pip install -e ".[dev]"
```

**Memory budget** (4-bit quantization):
- Llama-3-70B-Instruct (Q4): ~40 GB VRAM → fits L40S (48 GB)
- Llama-3-8B: ~5 GB VRAM
- CodeLlama-7B: ~4.5 GB VRAM
- Mistral-7B-v0.3: ~4.5 GB VRAM

### 1.2 vLLM Serving Stack

Each model runs as a separate vLLM OpenAI-compatible server. Use docker-compose or systemd:

```bash
# Setup A — Monolithic 70B (port 8000)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-70B-Instruct \
  --quantization awq \
  --max-model-len 4096 \
  --port 8000

# Setup B — Llama-3-8B (port 8001), CodeLlama-7B (port 8002), Mistral-7B (port 8003)
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct --port 8001
python -m vllm.entrypoints.openai.api_server \
  --model codellama/CodeLlama-7b-Instruct-hf --port 8002
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.3 --port 8003

# Setup C uses 8B drafter (port 8001) + 70B verifier (port 8000)
```

See `infrastructure/vllm/docker-compose.yml` for the full service definitions.

### 1.3 Environment Variables

```bash
# .env (git-ignored)
VLLM_LLAMA70B_URL=http://localhost:8000/v1
VLLM_LLAMA8B_URL=http://localhost:8001/v1
VLLM_CODELLAMA_URL=http://localhost:8002/v1
VLLM_MISTRAL_URL=http://localhost:8003/v1
MLFLOW_TRACKING_URI=http://localhost:5000
CODECARBON_PROJECT_NAME=thesis_benchmark
```

### 1.4 Verification Checklist

- [ ] `nvidia-smi` shows L40S with 48GB free
- [ ] All four vLLM servers respond to `/v1/models`
- [ ] MLflow UI accessible at port 5000
- [ ] `pytest tests/ -v` → 13 passed
- [ ] CodeCarbon writes to `./emissions.csv`
- [ ] NVML binds to GPU 0 without error

---

## WP2: Pilot Study (100 Stratified Queries)

**Purpose**: Calibrate the confidence threshold for Setup A (routing) and Setup C (speculative decoding) before committing to the full 1,664-query run.

### 2.1 Stratified Sample Construction

Draw from the custom stratified dataset (`benchmarks/custom_stratified.py`):
- Easy: 30 queries (30%)
- Medium: 40 queries (40%)
- Hard: 30 queries (30%)

### 2.2 Threshold Sweep

Test thresholds: **0.70, 0.75, 0.80** for both Setup A and Setup C.

```bash
python experiments/pilot_study.py \
  --n-queries 100 \
  --thresholds 0.70 0.75 0.80 \
  --output pilot_results/
```

### 2.3 Decision Criteria

Select threshold that maximizes EATS score subject to accuracy ≥ 85% of Llama-3-70B baseline on the 100-query pilot.

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
| HumanEval | 164 | 164 | All (code exec required) |
| Custom Stratified | 1,000 | 1,000 | Fixed split (300/400/300) |

Total: **2,664 queries × 3 setups = 7,992 inference calls** (minimum; Setup B and C make additional internal calls).

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

Or in parallel (requires enough VRAM — only C uses both 8B + 70B simultaneously):
```bash
python experiments/run_experiment.py --architecture all
```

### 3.3 Metrics Collected Per Query

| Metric | Source | Field |
|--------|--------|-------|
| Correct/incorrect | Ground truth comparison | `SampleResult.correct` |
| Latency (ms) | Wall clock | `Response.latency_ms` |
| LLM calls | Architecture counter | `Response.llm_calls` |
| Token count | vLLM response | `Response.total_tokens` |
| Energy (kWh) | CodeCarbon + NVML | `Response.energy_kwh` |
| CO2 (g) | CodeCarbon | `Response.co2_g` |
| Cost (USD) | Token pricing | `Response.cost_usd` |

### 3.4 MLflow Experiment Structure

```
mlflow/
  experiments/
    setup_a_mmlu/          run_id, accuracy, eats, p95_latency, energy_kwh
    setup_a_gsm8k/
    setup_a_humaneval/
    setup_b_mmlu/
    ...
    setup_c_humaneval/
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
- [ ] `architectures/monolithic.py` — **Setup A**: Llama-3-70B single-pass via vLLM
- [ ] `architectures/multi_agent_crew.py` — **Setup B**: CrewAI+LangGraph multi-agent
- [ ] `architectures/speculative_decoding.py` — **Setup C**: token-level draft-verify

### Benchmarks

- [x] `benchmarks/mmlu.py`
- [x] `benchmarks/gsm8k.py`
- [x] `benchmarks/hellaswag.py`
- [x] `benchmarks/arc.py`
- [x] `benchmarks/truthfulqa.py`
- [ ] `benchmarks/humaneval.py` — HumanEval (164 code problems)
- [ ] `benchmarks/custom_stratified.py` — Easy/Medium/Hard stratified set

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

- [x] `infrastructure/terraform/` — AWS VPC/EC2/S3/ECR/DynamoDB
- [ ] `infrastructure/vllm/docker-compose.yml` — vLLM multi-model serving
- [ ] `infrastructure/vllm/serve_model.sh` — launch helper scripts

### Analysis

- [ ] `analysis/statistical_analysis.py` — main analysis runner
- [ ] `analysis/pareto_plot.py` — Pareto frontier visualization
- [ ] `analysis/energy_report.py` — energy/CO2 summary

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| L40S OOM for 70B + 8B simultaneously | Medium | High | Run Setup A and C on separate VRAM windows; don't load both concurrently |
| vLLM version incompatibility | Low | Medium | Pin `vllm==0.4.3` in requirements |
| HumanEval code execution sandbox escape | Low | High | Run in Docker with `--network none` |
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
