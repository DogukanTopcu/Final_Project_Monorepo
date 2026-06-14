# Experiment Report — exp_589dd0a4
**Date:** 2026-06-10T22:09:15.475051+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | entropy_blackboard |
| Benchmark | truthfulqa |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 73.00% |
| 95% CI | [63.57%, 80.73%] |
| Correct / Total | 73 / 100 |
| Escalation Rate | 66.00% |
| ECE (confidence calibration) | 0.0984 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2975.8 |
| Model avg (ms) | 7839.3 |
| Summed model avg (ms) | 7839.3 |
| Model p50 (ms) | 4959.2 |
| Model p95 (ms) | 22057.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003104 |
| Total cost (USD) | $0.3104 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3104 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0532 |
| Escalated-path total (SLM+LLM) | $0.2571 |
| SLM-path cost fraction | 17.15% |
| Normalized cost (vs baseline) | 0.5332 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.936626 J/tok |
| Total energy (kWh) | 0.038469 |
| Avg energy per sample (kWh) | 0.00038469 |
| Total CO₂ (g) | 14.6183 |
| Avg CO₂ per sample (g) | 0.146183 |
| Normalized energy (vs baseline) | 0.6499 |

## EATS Score
**EATS = 0.4593**  
Normalized efficiency penalty: 0.8594  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.