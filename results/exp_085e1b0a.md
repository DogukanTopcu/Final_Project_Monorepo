# Experiment Report — exp_085e1b0a
**Date:** 2026-05-29T12:29:34.694393+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | gpt-oss-20b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 79.80% |
| 95% CI | [76.06%, 83.09%] |
| Correct / Total | 399 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0681 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 52611.8 |
| Model avg (ms) | 3544.9 |
| Summed model avg (ms) | 3544.9 |
| Model p50 (ms) | 2884.6 |
| Model p95 (ms) | 9901.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002990 |
| Total cost (USD) | $1.4949 |
| API cost (USD) | $0.3379 |
| Infra cost (USD) | $1.1570 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.3379 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.4949 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.041142 J/tok |
| Total energy (kWh) | 0.157550 |
| Avg energy per sample (kWh) | 0.00031510 |
| Total CO₂ (g) | 59.8689 |
| Avg CO₂ per sample (g) | 0.119738 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6049**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.1212  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.