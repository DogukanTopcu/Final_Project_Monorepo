# Experiment Report — exp_f164f3df
**Date:** 2026-06-01T09:06:03.479361+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
| SLM | None |
| LLM | qwen3.5-35b-a3b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2011 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 96.40% |
| 95% CI | [94.38%, 97.71%] |
| Correct / Total | 482 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0211 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 38930.5 |
| Model avg (ms) | 4510.5 |
| Summed model avg (ms) | 4510.5 |
| Model p50 (ms) | 4249.6 |
| Model p95 (ms) | 6242.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002944 |
| Total cost (USD) | $1.4722 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $1.4722 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.4722 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.109885 J/tok |
| Total energy (kWh) | 0.200465 |
| Avg energy per sample (kWh) | 0.00040093 |
| Total CO₂ (g) | 76.1768 |
| Avg CO₂ per sample (g) | 0.152354 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6957**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0216  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.