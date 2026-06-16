# Experiment Report — exp_ac21ba45
**Date:** 2026-05-29T14:23:07.409052+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
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
| Accuracy | 94.80% |
| 95% CI | [92.49%, 96.43%] |
| Correct / Total | 474 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.1880 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 57881.7 |
| Model avg (ms) | 3943.7 |
| Summed model avg (ms) | 3943.7 |
| Model p50 (ms) | 3551.0 |
| Model p95 (ms) | 6497.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003364 |
| Total cost (USD) | $1.6822 |
| API cost (USD) | $0.3950 |
| Infra cost (USD) | $1.2872 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.3950 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.6822 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.764259 J/tok |
| Total energy (kWh) | 0.175276 |
| Avg energy per sample (kWh) | 0.00035055 |
| Total CO₂ (g) | 66.6047 |
| Avg CO₂ per sample (g) | 0.133209 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6874**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0312  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.