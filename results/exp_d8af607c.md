# Experiment Report — exp_d8af607c
**Date:** 2026-06-04T14:44:25.196259+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | arc |
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
| Accuracy | 96.00% |
| 95% CI | [90.16%, 98.43%] |
| Correct / Total | 96 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0518 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2213.5 |
| Model avg (ms) | 21425.1 |
| Summed model avg (ms) | 19262.6 |
| Model p50 (ms) | 19191.3 |
| Model p95 (ms) | 39573.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004013 |
| Total cost (USD) | $0.4013 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.4013 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4013 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.924428 J/tok |
| Total energy (kWh) | 0.038525 |
| Avg energy per sample (kWh) | 0.00038525 |
| Total CO₂ (g) | 14.6396 |
| Avg CO₂ per sample (g) | 0.146396 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6936**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0240  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.