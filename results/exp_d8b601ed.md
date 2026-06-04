# Experiment Report — exp_d8b601ed
**Date:** 2026-06-03T21:38:29.151271+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | mmlu |
| SLM | None |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 50.00% |
| 95% CI | [23.66%, 76.34%] |
| Correct / Total | 5 / 10 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.3253 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 260.4 |
| Wall-clock avg (ms) | 19139.4 |
| Algorithmic avg (ms) | 23339.0 |
| Wall-clock p50 (ms) | 18131.5 |
| Wall-clock p95 (ms) | 33340.6 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004862 |
| Total cost (USD) | $0.0486 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0486 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0486 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.371601 J/tok |
| Total energy (kWh) | 0.004668 |
| Avg energy per sample (kWh) | 0.00046678 |
| Total CO₂ (g) | 1.7738 |
| Avg CO₂ per sample (g) | 0.177376 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.3333**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 50.00% | 10 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| business_ethics | 0.00% | 1 |
| conceptual_physics | 100.00% | 1 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 0.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| professional_accounting | 0.00% | 1 |
| professional_law | 0.00% | 2 |