# Experiment Report — exp_f851ec0e
**Date:** 2026-06-10T19:23:04.794233+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | entropy_blackboard |
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
| Accuracy | 83.00% |
| 95% CI | [74.45%, 89.11%] |
| Correct / Total | 83 / 100 |
| Escalation Rate | 32.00% |
| ECE (confidence calibration) | 0.0405 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2778.8 |
| Model avg (ms) | 13438.0 |
| Summed model avg (ms) | 13438.0 |
| Model p50 (ms) | 9812.9 |
| Model p95 (ms) | 34961.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003690 |
| Total cost (USD) | $0.3690 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3690 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1674 |
| Escalated-path total (SLM+LLM) | $0.2016 |
| SLM-path cost fraction | 45.37% |
| Normalized cost (vs baseline) | 0.4552 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.922090 J/tok |
| Total energy (kWh) | 0.040682 |
| Avg energy per sample (kWh) | 0.00040682 |
| Total CO₂ (g) | 15.4591 |
| Avg CO₂ per sample (g) | 0.154591 |
| Normalized energy (vs baseline) | 0.4646 |

## EATS Score
**EATS = 0.6849**  
Normalized efficiency penalty: 0.6996  
Accuracy deficit penalty: 0.1020  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.