# Experiment Report — exp_4d2795fa
**Date:** 2026-06-03T22:46:21.982815+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | arc |
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
| Accuracy | 91.00% |
| 95% CI | [83.77%, 95.19%] |
| Correct / Total | 91 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0380 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 4330.3 |
| Model avg (ms) | 15887.2 |
| Summed model avg (ms) | 33479.7 |
| Model p50 (ms) | 12979.2 |
| Model p95 (ms) | 35674.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006975 |
| Total cost (USD) | $0.6975 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6975 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.6975 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.503895 J/tok |
| Total energy (kWh) | 0.066959 |
| Avg energy per sample (kWh) | 0.00066959 |
| Total CO₂ (g) | 25.4446 |
| Avg CO₂ per sample (g) | 0.254446 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6672**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0540  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 91.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |