# Experiment Report — exp_61cab72b
**Date:** 2026-06-04T21:45:31.846138+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | speculative |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
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
| Accuracy | 100.00% |
| 95% CI | [72.25%, 100.00%] |
| Correct / Total | 10 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.1445 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 258.2 |
| Wall-clock avg (ms) | 25565.8 |
| Algorithmic avg (ms) | 25557.5 |
| Wall-clock p50 (ms) | 24919.7 |
| Wall-clock p95 (ms) | 53981.1 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.008837 |
| Total cost (USD) | $0.0884 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0884 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0884 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0901 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.758000 J/tok |
| Total energy (kWh) | 0.010556 |
| Avg energy per sample (kWh) | 0.00105563 |
| Total CO₂ (g) | 4.0114 |
| Avg CO₂ per sample (g) | 0.401141 |
| Normalized energy (vs baseline) | 1.2056 |

## EATS Score
**EATS = 0.3651**  
Normalized efficiency penalty: 1.7390  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| business_ethics | 100.00% | 1 |
| conceptual_physics | 100.00% | 1 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 100.00% | 2 |