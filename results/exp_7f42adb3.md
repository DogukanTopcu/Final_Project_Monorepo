# Experiment Report — exp_7f42adb3
**Date:** 2026-06-05T15:48:17.840083+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | hellaswag |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.8 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 90.00% |
| 95% CI | [82.56%, 94.48%] |
| Correct / Total | 90 / 100 |
| Escalation Rate | 91.00% |
| ECE (confidence calibration) | 0.2180 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2725.7 |
| Model avg (ms) | 1584.9 |
| Summed model avg (ms) | 1584.9 |
| Model p50 (ms) | 1570.0 |
| Model p95 (ms) | 2060.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000607 |
| Total cost (USD) | $0.0607 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0607 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0018 |
| Escalated-path total (SLM+LLM) | $0.0589 |
| SLM-path cost fraction | 3.01% |
| Normalized cost (vs baseline) | 0.0897 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.219934 J/tok |
| Total energy (kWh) | 0.007464 |
| Avg energy per sample (kWh) | 0.00007464 |
| Total CO₂ (g) | 2.8363 |
| Avg CO₂ per sample (g) | 0.028363 |
| Normalized energy (vs baseline) | 0.1030 |

## EATS Score
**EATS = 0.8690**  
Normalized efficiency penalty: 0.1356  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 88.89% | 9 |
| LLM-handled (escalated) | 90.11% | 91 |
| Escalation rate | 91.00% | — |