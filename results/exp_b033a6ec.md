# Experiment Report — exp_b033a6ec
**Date:** 2026-06-09T21:23:23.151583+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | gsm8k |
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
| Accuracy | 97.00% |
| 95% CI | [91.55%, 98.97%] |
| Correct / Total | 97 / 100 |
| Escalation Rate | 16.00% |
| ECE (confidence calibration) | 0.0973 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2546.0 |
| Model avg (ms) | 11804.4 |
| Summed model avg (ms) | 11804.4 |
| Model p50 (ms) | 8825.1 |
| Model p95 (ms) | 29377.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002684 |
| Total cost (USD) | $0.2684 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2684 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1840 |
| Escalated-path total (SLM+LLM) | $0.0843 |
| SLM-path cost fraction | 68.58% |
| Normalized cost (vs baseline) | 0.3610 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.244439 J/tok |
| Total energy (kWh) | 0.027086 |
| Avg energy per sample (kWh) | 0.00027086 |
| Total CO₂ (g) | 10.2926 |
| Avg CO₂ per sample (g) | 0.102926 |
| Normalized energy (vs baseline) | 0.3465 |

## EATS Score
**EATS = 0.7855**  
Normalized efficiency penalty: 0.6173  
Accuracy deficit penalty: 0.0180  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.