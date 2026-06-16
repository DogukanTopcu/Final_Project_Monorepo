# Experiment Report — exp_3d15e23b
**Date:** 2026-06-04T13:14:19.319873+00:00  

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
| Model avg (ms) | 26887.0 |
| Summed model avg (ms) | 24656.7 |
| Model p50 (ms) | 24168.1 |
| Model p95 (ms) | 47750.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

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
**EATS = 0.7143**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0000  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.