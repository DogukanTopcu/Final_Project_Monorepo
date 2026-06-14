# Experiment Report — exp_509abf4c
**Date:** 2026-06-04T23:09:21.477199+00:00  

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
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 82.00% |
| 95% CI | [73.33%, 88.30%] |
| Correct / Total | 82 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0325 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2925.0 |
| Model avg (ms) | 2462.3 |
| Summed model avg (ms) | 2462.3 |
| Model p50 (ms) | 2011.4 |
| Model p95 (ms) | 5904.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001070 |
| Total cost (USD) | $0.1070 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1070 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.1070 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 0.1320 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.780784 J/tok |
| Total energy (kWh) | 0.013565 |
| Avg energy per sample (kWh) | 0.00013565 |
| Total CO₂ (g) | 5.1548 |
| Avg CO₂ per sample (g) | 0.051548 |
| Normalized energy (vs baseline) | 0.1549 |

## EATS Score
**EATS = 0.8232**  
Normalized efficiency penalty: 0.1703  
Accuracy deficit penalty: 0.1080  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Speculative Breakdown
| Metric | Value |
|--------|-------|
| Rewrite rate | 100.00% |
| Avg accepted draft ratio | 8.33% |
| Avg draft completion tokens | 29.1 |
| Max draft completion tokens | 64 |
| Avg verifier requests | 2.07 |
| Avg verifier completion tokens | 42.9 |