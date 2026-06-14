# Experiment Report — exp_ab84730c
**Date:** 2026-06-12T20:55:25.637382+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | entropy_blackboard |
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
| Accuracy | 92.00% |
| 95% CI | [85.00%, 95.89%] |
| Correct / Total | 92 / 100 |
| Escalation Rate | 15.00% |
| ECE (confidence calibration) | 0.1133 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2733.0 |
| Model avg (ms) | 8041.6 |
| Summed model avg (ms) | 8041.6 |
| Model p50 (ms) | 6179.8 |
| Model p95 (ms) | 24980.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001997 |
| Total cost (USD) | $0.1997 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1997 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1328 |
| Escalated-path total (SLM+LLM) | $0.0668 |
| SLM-path cost fraction | 66.53% |
| Normalized cost (vs baseline) | 0.3079 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.450514 J/tok |
| Total energy (kWh) | 0.021065 |
| Avg energy per sample (kWh) | 0.00021065 |
| Total CO₂ (g) | 8.0048 |
| Avg CO₂ per sample (g) | 0.080048 |
| Normalized energy (vs baseline) | 0.2951 |

## EATS Score
**EATS = 0.6136**  
Normalized efficiency penalty: 0.5793  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.