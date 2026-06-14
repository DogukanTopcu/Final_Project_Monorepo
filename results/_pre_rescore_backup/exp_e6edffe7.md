# Experiment Report — exp_e6edffe7
**Date:** 2026-06-05T20:19:20.491235+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
| Benchmark | truthfulqa |
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
| Escalation Rate | 72.00% |
| ECE (confidence calibration) | 0.1157 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2549.1 |
| Model avg (ms) | 8622.0 |
| Summed model avg (ms) | 8622.0 |
| Model p50 (ms) | 6119.5 |
| Model p95 (ms) | 27176.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001985 |
| Total cost (USD) | $0.1985 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1985 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0117 |
| Escalated-path total (SLM+LLM) | $0.1869 |
| SLM-path cost fraction | 5.87% |
| Normalized cost (vs baseline) | 0.3411 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.304370 J/tok |
| Total energy (kWh) | 0.020173 |
| Avg energy per sample (kWh) | 0.00020173 |
| Total CO₂ (g) | 7.6658 |
| Avg CO₂ per sample (g) | 0.076658 |
| Normalized energy (vs baseline) | 0.3408 |

## EATS Score
**EATS = 0.4905**  
Normalized efficiency penalty: 0.7477  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 72.00% |
| LLM calls total | 72 |