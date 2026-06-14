# Experiment Report — exp_a324cae7
**Date:** 2026-06-04T14:08:34.997256+00:00  

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
| Accuracy | 79.00% |
| 95% CI | [70.02%, 85.83%] |
| Correct / Total | 79 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1251 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2351.4 |
| Model avg (ms) | 28132.2 |
| Summed model avg (ms) | 25985.0 |
| Model p50 (ms) | 23500.7 |
| Model p95 (ms) | 67977.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005414 |
| Total cost (USD) | $0.5414 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5414 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.5414 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.828254 J/tok |
| Total energy (kWh) | 0.051970 |
| Avg energy per sample (kWh) | 0.00051970 |
| Total CO₂ (g) | 19.7486 |
| Avg CO₂ per sample (g) | 0.197486 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6003**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.1260  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.