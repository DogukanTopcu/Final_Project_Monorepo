# Experiment Report — exp_d508c1f0
**Date:** 2026-06-01T23:40:59.719612+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | truthfulqa |
| SLM | None |
| LLM | gpt-oss-120b |
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
| Accuracy | 82.40% |
| 95% CI | [78.82%, 85.49%] |
| Correct / Total | 412 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0394 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 32155.6 |
| Model avg (ms) | 2991.2 |
| Summed model avg (ms) | 2991.2 |
| Model p50 (ms) | 2819.5 |
| Model p95 (ms) | 4328.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.007099 |
| Total cost (USD) | $3.5496 |
| API cost (USD) | $0.8493 |
| Infra cost (USD) | $2.7004 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.8493 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $3.5496 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 9.329645 J/tok |
| Total energy (kWh) | 0.249267 |
| Avg energy per sample (kWh) | 0.00049853 |
| Total CO₂ (g) | 94.7216 |
| Avg CO₂ per sample (g) | 0.189443 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6197**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.1056  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.