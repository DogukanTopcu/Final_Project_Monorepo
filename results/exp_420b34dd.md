# Experiment Report — exp_420b34dd
**Date:** 2026-06-09T20:39:54.888271+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | hellaswag |
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
| Accuracy | 79.00% |
| 95% CI | [70.02%, 85.83%] |
| Correct / Total | 79 / 100 |
| Escalation Rate | 41.00% |
| ECE (confidence calibration) | 0.0343 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2807.5 |
| Model avg (ms) | 8615.0 |
| Summed model avg (ms) | 8615.0 |
| Model p50 (ms) | 7392.1 |
| Model p95 (ms) | 16204.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002861 |
| Total cost (USD) | $0.2861 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2861 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1158 |
| Escalated-path total (SLM+LLM) | $0.1703 |
| SLM-path cost fraction | 40.47% |
| Normalized cost (vs baseline) | 0.4227 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.023425 J/tok |
| Total energy (kWh) | 0.033750 |
| Avg energy per sample (kWh) | 0.00033750 |
| Total CO₂ (g) | 12.8252 |
| Avg CO₂ per sample (g) | 0.128252 |
| Normalized energy (vs baseline) | 0.4658 |

## EATS Score
**EATS = 0.5353**  
Normalized efficiency penalty: 0.6859  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.