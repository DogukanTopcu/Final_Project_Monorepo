# Experiment Report — exp_9bedaa07
**Date:** 2026-06-08T20:12:38.919057+00:00  

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
| Accuracy | 74.00% |
| 95% CI | [64.63%, 81.60%] |
| Correct / Total | 74 / 100 |
| Escalation Rate | 20.00% |
| ECE (confidence calibration) | 0.1280 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2649.2 |
| Model avg (ms) | 12953.3 |
| Summed model avg (ms) | 12953.3 |
| Model p50 (ms) | 11088.0 |
| Model p95 (ms) | 32332.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003113 |
| Total cost (USD) | $0.3113 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3113 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1988 |
| Escalated-path total (SLM+LLM) | $0.1125 |
| SLM-path cost fraction | 63.86% |
| Normalized cost (vs baseline) | 0.3839 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.390831 J/tok |
| Total energy (kWh) | 0.032322 |
| Avg energy per sample (kWh) | 0.00032322 |
| Total CO₂ (g) | 12.2824 |
| Avg CO₂ per sample (g) | 0.122824 |
| Normalized energy (vs baseline) | 0.3691 |

## EATS Score
**EATS = 0.6453**  
Normalized efficiency penalty: 0.6269  
Accuracy deficit penalty: 0.1560  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.