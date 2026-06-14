# Experiment Report — exp_6040fcf0
**Date:** 2026-06-08T17:47:32.110463+00:00  

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
| N Samples | 20 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 80.00% |
| 95% CI | [58.40%, 91.93%] |
| Correct / Total | 16 / 20 |
| Escalation Rate | 50.00% |
| ECE (confidence calibration) | 0.1059 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 574.8 |
| Model avg (ms) | 10110.6 |
| Summed model avg (ms) | 10110.6 |
| Model p50 (ms) | 6476.5 |
| Model p95 (ms) | 37314.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003460 |
| Total cost (USD) | $0.0692 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0692 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0218 |
| Escalated-path total (SLM+LLM) | $0.0474 |
| SLM-path cost fraction | 31.51% |
| Normalized cost (vs baseline) | 0.4269 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.105162 J/tok |
| Total energy (kWh) | 0.008242 |
| Avg energy per sample (kWh) | 0.00041210 |
| Total CO₂ (g) | 3.1320 |
| Avg CO₂ per sample (g) | 0.156598 |
| Normalized energy (vs baseline) | 0.4706 |

## EATS Score
**EATS = 0.6898**  
Normalized efficiency penalty: 0.5994  
Accuracy deficit penalty: 0.1200  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.