# Experiment Report — exp_cc0c1be2
**Date:** 2026-06-01T20:41:12.642686+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | hellaswag |
| SLM | None |
| LLM | llama3.3-70b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 89.00% |
| 95% CI | [81.37%, 93.75%] |
| Correct / Total | 89 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0574 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1999.2 |
| Model avg (ms) | 7446.3 |
| Summed model avg (ms) | 7446.3 |
| Model p50 (ms) | 6128.2 |
| Model p95 (ms) | 13632.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.013800 |
| Total cost (USD) | $1.3800 |
| API cost (USD) | $0.0355 |
| Infra cost (USD) | $1.3445 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0355 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.3800 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 30.011390 J/tok |
| Total energy (kWh) | 0.124105 |
| Avg energy per sample (kWh) | 0.00124105 |
| Total CO₂ (g) | 47.1601 |
| Avg CO₂ per sample (g) | 0.471601 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6563**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0660  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.