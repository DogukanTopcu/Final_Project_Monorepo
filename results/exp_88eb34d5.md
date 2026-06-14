# Experiment Report — exp_88eb34d5
**Date:** 2026-06-03T20:49:49.423714+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | mmlu |
| SLM | None |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1784 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 75.00% |
| 95% CI | [65.70%, 82.45%] |
| Correct / Total | 75 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1380 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2447.6 |
| Model avg (ms) | 17604.6 |
| Summed model avg (ms) | 17604.6 |
| Model p50 (ms) | 14986.6 |
| Model p95 (ms) | 42530.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003668 |
| Total cost (USD) | $0.3668 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3668 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.3668 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.941662 J/tok |
| Total energy (kWh) | 0.035209 |
| Avg energy per sample (kWh) | 0.00035209 |
| Total CO₂ (g) | 13.3795 |
| Avg CO₂ per sample (g) | 0.133795 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.5769**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.1500  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 75.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |