# Experiment Report — exp_bb82ebef
**Date:** 2026-06-13T00:53:55.016029+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | gsm8k |
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
| Accuracy | 94.00% |
| 95% CI | [87.52%, 97.22%] |
| Correct / Total | 94 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0601 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2564.0 |
| Model avg (ms) | 7093.2 |
| Summed model avg (ms) | 7093.2 |
| Model p50 (ms) | 5947.4 |
| Model p95 (ms) | 14734.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001478 |
| Total cost (USD) | $0.1478 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1478 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1478 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.1988 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.808111 J/tok |
| Total energy (kWh) | 0.014186 |
| Avg energy per sample (kWh) | 0.00014186 |
| Total CO₂ (g) | 5.3908 |
| Avg CO₂ per sample (g) | 0.053908 |
| Normalized energy (vs baseline) | 0.1815 |

## EATS Score
**EATS = 0.8408**  
Normalized efficiency penalty: 0.3551  
Accuracy deficit penalty: 0.0360  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.