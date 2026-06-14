# Experiment Report — exp_71bbd2d0
**Date:** 2026-06-04T09:48:34.438470+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | gsm8k |
| SLM | None |
| LLM | None |
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
| Accuracy | 96.00% |
| 95% CI | [90.16%, 98.43%] |
| Correct / Total | 96 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0602 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 6936.3 |
| Model avg (ms) | 16147.3 |
| Summed model avg (ms) | 43770.8 |
| Model p50 (ms) | 14513.9 |
| Model p95 (ms) | 29501.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.009119 |
| Total cost (USD) | $0.9119 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.9119 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.9119 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.813784 J/tok |
| Total energy (kWh) | 0.087542 |
| Avg energy per sample (kWh) | 0.00087542 |
| Total CO₂ (g) | 33.2658 |
| Avg CO₂ per sample (g) | 0.332658 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6936**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0240  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 96.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |