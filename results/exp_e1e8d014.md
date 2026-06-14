# Experiment Report — exp_e1e8d014
**Date:** 2026-06-07T21:30:31.717300+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 80.00% |
| 95% CI | [49.02%, 94.33%] |
| Correct / Total | 8 / 10 |
| Escalation Rate | 20.00% |
| ECE (confidence calibration) | 0.1225 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 289.9 |
| Model avg (ms) | 6460.8 |
| Summed model avg (ms) | 6460.8 |
| Model p50 (ms) | 3964.4 |
| Model p95 (ms) | 22657.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002446 |
| Total cost (USD) | $0.0245 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0245 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0067 |
| Escalated-path total (SLM+LLM) | $0.0177 |
| SLM-path cost fraction | 27.52% |
| Normalized cost (vs baseline) | 0.3909 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.760030 J/tok |
| Total energy (kWh) | 0.002997 |
| Avg energy per sample (kWh) | 0.00029968 |
| Total CO₂ (g) | 1.1388 |
| Avg CO₂ per sample (g) | 0.113879 |
| Normalized energy (vs baseline) | 0.3518 |

## EATS Score
**EATS = 0.7295**  
Normalized efficiency penalty: 0.4417  
Accuracy deficit penalty: 0.1200  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.