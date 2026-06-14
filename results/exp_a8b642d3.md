# Experiment Report — exp_a8b642d3
**Date:** 2026-06-05T21:22:05.601683+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
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
| Accuracy | 72.00% |
| 95% CI | [62.51%, 79.86%] |
| Correct / Total | 72 / 100 |
| Escalation Rate | 42.00% |
| ECE (confidence calibration) | 0.1436 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2531.7 |
| Model avg (ms) | 10191.5 |
| Summed model avg (ms) | 10191.5 |
| Model p50 (ms) | 5384.5 |
| Model p95 (ms) | 32792.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002215 |
| Total cost (USD) | $0.2215 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2215 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0662 |
| Escalated-path total (SLM+LLM) | $0.1553 |
| SLM-path cost fraction | 29.88% |
| Normalized cost (vs baseline) | 0.2732 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.042234 J/tok |
| Total energy (kWh) | 0.021804 |
| Avg energy per sample (kWh) | 0.00021804 |
| Total CO₂ (g) | 8.2857 |
| Avg CO₂ per sample (g) | 0.082857 |
| Normalized energy (vs baseline) | 0.2490 |

## EATS Score
**EATS = 0.6696**  
Normalized efficiency penalty: 0.4683  
Accuracy deficit penalty: 0.1680  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 42.00% |
| LLM calls total | 42 |