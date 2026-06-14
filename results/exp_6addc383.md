# Experiment Report — exp_6addc383
**Date:** 2026-06-05T15:38:31.922067+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | arc |
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
| Accuracy | 91.00% |
| 95% CI | [83.77%, 95.19%] |
| Correct / Total | 91 / 100 |
| Escalation Rate | 75.00% |
| ECE (confidence calibration) | 0.2113 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2748.6 |
| Model avg (ms) | 1382.5 |
| Summed model avg (ms) | 1382.5 |
| Model p50 (ms) | 1403.7 |
| Model p95 (ms) | 2035.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000519 |
| Total cost (USD) | $0.0519 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0519 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0046 |
| Escalated-path total (SLM+LLM) | $0.0473 |
| SLM-path cost fraction | 8.83% |
| Normalized cost (vs baseline) | 0.0800 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.009554 J/tok |
| Total energy (kWh) | 0.006343 |
| Avg energy per sample (kWh) | 0.00006343 |
| Total CO₂ (g) | 2.4105 |
| Avg CO₂ per sample (g) | 0.024105 |
| Normalized energy (vs baseline) | 0.0889 |

## EATS Score
**EATS = 0.9037**  
Normalized efficiency penalty: 0.1073  
Accuracy deficit penalty: 0.0540  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 76.00% | 25 |
| LLM-handled (escalated) | 96.00% | 75 |
| Escalation rate | 75.00% | — |