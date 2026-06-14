# Experiment Report — exp_f8641bf1
**Date:** 2026-06-05T19:48:54.780988+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
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
| Accuracy | 92.00% |
| 95% CI | [85.00%, 95.89%] |
| Correct / Total | 92 / 100 |
| Escalation Rate | 4.00% |
| ECE (confidence calibration) | 0.0375 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2493.8 |
| Model avg (ms) | 12889.8 |
| Summed model avg (ms) | 12889.8 |
| Model p50 (ms) | 5271.1 |
| Model p95 (ms) | 27114.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002692 |
| Total cost (USD) | $0.2692 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2692 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1225 |
| Escalated-path total (SLM+LLM) | $0.1467 |
| SLM-path cost fraction | 45.50% |
| Normalized cost (vs baseline) | 0.3621 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.897989 J/tok |
| Total energy (kWh) | 0.025877 |
| Avg energy per sample (kWh) | 0.00025877 |
| Total CO₂ (g) | 9.8331 |
| Avg CO₂ per sample (g) | 0.098331 |
| Normalized energy (vs baseline) | 0.3310 |

## EATS Score
**EATS = 0.7502**  
Normalized efficiency penalty: 0.6461  
Accuracy deficit penalty: 0.0480  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 4.00% |
| LLM calls total | 4 |