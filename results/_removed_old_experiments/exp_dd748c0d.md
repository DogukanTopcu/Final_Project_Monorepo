# Experiment Report — exp_dd748c0d
**Date:** 2026-06-03T20:27:27.627909+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | mmlu |
| SLM | None |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1312 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 57.00% |
| 95% CI | [47.22%, 66.27%] |
| Correct / Total | 57 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.3080 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2254.3 |
| Model avg (ms) | 3536.8 |
| Summed model avg (ms) | 3536.8 |
| Model p50 (ms) | 2103.7 |
| Model p95 (ms) | 13973.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000737 |
| Total cost (USD) | $0.0737 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0737 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0737 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.193893 J/tok |
| Total energy (kWh) | 0.007074 |
| Avg energy per sample (kWh) | 0.00007074 |
| Total CO₂ (g) | 2.6880 |
| Avg CO₂ per sample (g) | 0.026880 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4642**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.2580  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 57.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |