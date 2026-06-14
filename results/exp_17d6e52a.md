# Experiment Report — exp_17d6e52a
**Date:** 2026-06-12T23:52:56.475662+00:00  

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
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 75.00% |
| 95% CI | [65.70%, 82.45%] |
| Correct / Total | 75 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0860 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2657.7 |
| Model avg (ms) | 12309.4 |
| Summed model avg (ms) | 12309.4 |
| Model p50 (ms) | 7041.2 |
| Model p95 (ms) | 48730.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002564 |
| Total cost (USD) | $0.2564 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2564 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.2564 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3163 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.709156 J/tok |
| Total energy (kWh) | 0.024619 |
| Avg energy per sample (kWh) | 0.00024619 |
| Total CO₂ (g) | 9.3551 |
| Avg CO₂ per sample (g) | 0.093551 |
| Normalized energy (vs baseline) | 0.2812 |

## EATS Score
**EATS = 0.6687**  
Normalized efficiency penalty: 0.5537  
Accuracy deficit penalty: 0.1500  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.