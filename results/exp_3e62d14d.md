# Experiment Report — exp_3e62d14d
**Date:** 2026-06-09T20:10:08.507810+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | arc |
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
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 13.00% |
| ECE (confidence calibration) | 0.1392 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2593.2 |
| Model avg (ms) | 8335.2 |
| Summed model avg (ms) | 8335.2 |
| Model p50 (ms) | 5568.5 |
| Model p95 (ms) | 24233.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001936 |
| Total cost (USD) | $0.1936 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1936 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1435 |
| Escalated-path total (SLM+LLM) | $0.0501 |
| SLM-path cost fraction | 74.12% |
| Normalized cost (vs baseline) | 0.2986 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.292117 J/tok |
| Total energy (kWh) | 0.019766 |
| Avg energy per sample (kWh) | 0.00019766 |
| Total CO₂ (g) | 7.5112 |
| Avg CO₂ per sample (g) | 0.075112 |
| Normalized energy (vs baseline) | 0.2769 |

## EATS Score
**EATS = 0.6191**  
Normalized efficiency penalty: 0.5844  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.