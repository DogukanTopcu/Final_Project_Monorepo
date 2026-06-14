# Experiment Report — exp_c28bc724
**Date:** 2026-06-13T01:29:20.654888+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | truthfulqa |
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
| Accuracy | 67.00% |
| 95% CI | [57.31%, 75.44%] |
| Correct / Total | 67 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1057 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2634.8 |
| Model avg (ms) | 8807.9 |
| Summed model avg (ms) | 8807.9 |
| Model p50 (ms) | 6813.1 |
| Model p95 (ms) | 27659.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001835 |
| Total cost (USD) | $0.1835 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1835 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1835 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3153 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.732661 J/tok |
| Total energy (kWh) | 0.017616 |
| Avg energy per sample (kWh) | 0.00017616 |
| Total CO₂ (g) | 6.6940 |
| Avg CO₂ per sample (g) | 0.066940 |
| Normalized energy (vs baseline) | 0.2976 |

## EATS Score
**EATS = 0.4761**  
Normalized efficiency penalty: 0.7372  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.