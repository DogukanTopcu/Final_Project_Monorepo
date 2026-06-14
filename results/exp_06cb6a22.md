# Experiment Report — exp_06cb6a22
**Date:** 2026-06-04T23:59:20.630043+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | mmlu |
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
| Accuracy | 77.00% |
| 95% CI | [67.85%, 84.16%] |
| Correct / Total | 77 / 100 |
| Escalation Rate | 56.00% |
| ECE (confidence calibration) | 0.0968 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2726.5 |
| Model avg (ms) | 2473.5 |
| Summed model avg (ms) | 2473.5 |
| Model p50 (ms) | 1551.5 |
| Model p95 (ms) | 7799.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000805 |
| Total cost (USD) | $0.0805 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0805 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0177 |
| Escalated-path total (SLM+LLM) | $0.0628 |
| SLM-path cost fraction | 21.95% |
| Normalized cost (vs baseline) | 0.0993 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.036282 J/tok |
| Total energy (kWh) | 0.009435 |
| Avg energy per sample (kWh) | 0.00009435 |
| Total CO₂ (g) | 3.5852 |
| Avg CO₂ per sample (g) | 0.035852 |
| Normalized energy (vs baseline) | 0.1077 |

## EATS Score
**EATS = 0.7980**  
Normalized efficiency penalty: 0.1422  
Accuracy deficit penalty: 0.1380  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 75.00% | 44 |
| LLM-handled (escalated) | 78.57% | 56 |
| Escalation rate | 56.00% | — |