# Experiment Report — exp_f66818fe
**Date:** 2026-06-10T21:43:09.000449+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | entropy_blackboard |
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
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 26.00% |
| ECE (confidence calibration) | 0.0716 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2554.6 |
| Model avg (ms) | 12055.6 |
| Summed model avg (ms) | 12055.6 |
| Model p50 (ms) | 8953.0 |
| Model p95 (ms) | 32421.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002695 |
| Total cost (USD) | $0.2695 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2695 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1416 |
| Escalated-path total (SLM+LLM) | $0.1279 |
| SLM-path cost fraction | 52.55% |
| Normalized cost (vs baseline) | 0.3625 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.150282 J/tok |
| Total energy (kWh) | 0.026950 |
| Avg energy per sample (kWh) | 0.00026950 |
| Total CO₂ (g) | 10.2409 |
| Avg CO₂ per sample (g) | 0.102409 |
| Normalized energy (vs baseline) | 0.3448 |

## EATS Score
**EATS = 0.7724**  
Normalized efficiency penalty: 0.6250  
Accuracy deficit penalty: 0.0300  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.