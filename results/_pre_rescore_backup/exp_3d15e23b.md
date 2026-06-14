# Experiment Report — exp_3d15e23b
**Date:** 2026-06-04T13:14:19.313602+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 100.00% |
| 95% CI | [72.25%, 100.00%] |
| Correct / Total | 10 / 10 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0949 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 230.5 |
| Wall-clock avg (ms) | 26887.0 |
| Algorithmic avg (ms) | 24656.7 |
| Wall-clock p50 (ms) | 24168.1 |
| Wall-clock p95 (ms) | 47750.8 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005137 |
| Total cost (USD) | $0.0514 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0514 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0514 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.864743 J/tok |
| Total energy (kWh) | 0.004931 |
| Avg energy per sample (kWh) | 0.00049313 |
| Total CO₂ (g) | 1.8739 |
| Avg CO₂ per sample (g) | 0.187391 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.5000**  
Normalized efficiency penalty: 1.0000  

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