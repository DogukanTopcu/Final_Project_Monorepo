# Experiment Report — exp_5df4a7f6
**Date:** 2026-06-01T07:06:39.801070+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | qwen3.5-35b-a3b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2034 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 86.20% |
| 95% CI | [82.90%, 88.95%] |
| Correct / Total | 431 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0546 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 58380.3 |
| Model avg (ms) | 4270.7 |
| Summed model avg (ms) | 4270.7 |
| Model p50 (ms) | 3400.0 |
| Model p95 (ms) | 12338.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002788 |
| Total cost (USD) | $1.3939 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $1.3939 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.3939 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.740649 J/tok |
| Total energy (kWh) | 0.189810 |
| Avg energy per sample (kWh) | 0.00037962 |
| Total CO₂ (g) | 72.1277 |
| Avg CO₂ per sample (g) | 0.144255 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6410**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0828  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.