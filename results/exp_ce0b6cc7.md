# Experiment Report — exp_ce0b6cc7
**Date:** 2026-06-12T21:18:40.060967+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | entropy_blackboard |
| Benchmark | hellaswag |
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
| Accuracy | 84.00% |
| 95% CI | [75.58%, 89.90%] |
| Correct / Total | 84 / 100 |
| Escalation Rate | 80.00% |
| ECE (confidence calibration) | 0.0562 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 3202.8 |
| Model avg (ms) | 7649.0 |
| Summed model avg (ms) | 7649.0 |
| Model p50 (ms) | 6519.0 |
| Model p95 (ms) | 13833.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003697 |
| Total cost (USD) | $0.3697 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3697 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0516 |
| Escalated-path total (SLM+LLM) | $0.3181 |
| SLM-path cost fraction | 13.97% |
| Normalized cost (vs baseline) | 0.5463 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 7.039765 J/tok |
| Total energy (kWh) | 0.047906 |
| Avg energy per sample (kWh) | 0.00047906 |
| Total CO₂ (g) | 18.2041 |
| Avg CO₂ per sample (g) | 0.182041 |
| Normalized energy (vs baseline) | 0.6611 |

## EATS Score
**EATS = 0.6954**  
Normalized efficiency penalty: 0.6800  
Accuracy deficit penalty: 0.0960  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.