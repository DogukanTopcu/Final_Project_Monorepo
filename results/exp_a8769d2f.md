# Experiment Report — exp_a8769d2f
**Date:** 2026-06-09T22:06:51.512591+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
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
| Accuracy | 69.00% |
| 95% CI | [59.37%, 77.22%] |
| Correct / Total | 69 / 100 |
| Escalation Rate | 39.00% |
| ECE (confidence calibration) | 0.0975 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2699.3 |
| Model avg (ms) | 12968.0 |
| Summed model avg (ms) | 12968.0 |
| Model p50 (ms) | 9832.9 |
| Model p95 (ms) | 36251.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003660 |
| Total cost (USD) | $0.3660 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3660 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1453 |
| Escalated-path total (SLM+LLM) | $0.2207 |
| SLM-path cost fraction | 39.70% |
| Normalized cost (vs baseline) | 0.6289 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.195389 J/tok |
| Total energy (kWh) | 0.040793 |
| Avg energy per sample (kWh) | 0.00040793 |
| Total CO₂ (g) | 15.5014 |
| Avg CO₂ per sample (g) | 0.155014 |
| Normalized energy (vs baseline) | 0.6892 |

## EATS Score
**EATS = 0.5370**  
Normalized efficiency penalty: 1.0226  
Accuracy deficit penalty: 0.1860  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.