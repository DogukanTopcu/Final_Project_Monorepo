# Experiment Report — exp_3ef3b09b
**Date:** 2026-06-07T19:38:38.798753+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
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
| Accuracy | 83.00% |
| 95% CI | [74.45%, 89.11%] |
| Correct / Total | 83 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0796 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 3525.3 |
| Model avg (ms) | 7837.6 |
| Summed model avg (ms) | 7837.6 |
| Model p50 (ms) | 7514.3 |
| Model p95 (ms) | 11131.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005020 |
| Total cost (USD) | $0.5020 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5020 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.5020 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 0.8626 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 8.883405 J/tok |
| Total energy (kWh) | 0.068180 |
| Avg energy per sample (kWh) | 0.00068180 |
| Total CO₂ (g) | 25.9085 |
| Avg CO₂ per sample (g) | 0.259085 |
| Normalized energy (vs baseline) | 1.1519 |

## EATS Score
**EATS = 0.4247**  
Normalized efficiency penalty: 1.1244  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.