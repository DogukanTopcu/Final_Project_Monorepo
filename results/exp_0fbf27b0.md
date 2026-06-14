# Experiment Report — exp_0fbf27b0
**Date:** 2026-06-07T18:08:28.079414+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | mmlu |
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
| Accuracy | 79.00% |
| 95% CI | [70.02%, 85.83%] |
| Correct / Total | 79 / 100 |
| Escalation Rate | 29.00% |
| ECE (confidence calibration) | 0.1088 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2673.4 |
| Model avg (ms) | 23150.7 |
| Summed model avg (ms) | 23150.7 |
| Model p50 (ms) | 16776.3 |
| Model p95 (ms) | 67658.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006337 |
| Total cost (USD) | $0.6337 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6337 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.3783 |
| Escalated-path total (SLM+LLM) | $0.2554 |
| SLM-path cost fraction | 59.70% |
| Normalized cost (vs baseline) | 0.7817 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.058170 J/tok |
| Total energy (kWh) | 0.069767 |
| Avg energy per sample (kWh) | 0.00069767 |
| Total CO₂ (g) | 26.5114 |
| Avg CO₂ per sample (g) | 0.265114 |
| Normalized energy (vs baseline) | 0.7968 |

## EATS Score
**EATS = 0.5654**  
Normalized efficiency penalty: 1.2030  
Accuracy deficit penalty: 0.1260  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.