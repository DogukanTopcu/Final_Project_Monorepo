# Experiment Report — exp_6d35e6d9
**Date:** 2026-06-04T23:22:53.663947+00:00  

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
| N Samples | 20 |
| Confidence Threshold | 0.75 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 80.00% |
| 95% CI | [58.40%, 91.93%] |
| Correct / Total | 16 / 20 |
| Escalation Rate | 55.00% |
| ECE (confidence calibration) | 0.1959 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 548.4 |
| Model avg (ms) | 2326.8 |
| Summed model avg (ms) | 2326.8 |
| Model p50 (ms) | 1661.0 |
| Model p95 (ms) | 7834.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000776 |
| Total cost (USD) | $0.0155 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0155 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0045 |
| Escalated-path total (SLM+LLM) | $0.0110 |
| SLM-path cost fraction | 29.08% |
| Normalized cost (vs baseline) | 0.0957 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.170593 J/tok |
| Total energy (kWh) | 0.001833 |
| Avg energy per sample (kWh) | 0.00009163 |
| Total CO₂ (g) | 0.6964 |
| Avg CO₂ per sample (g) | 0.034821 |
| Normalized energy (vs baseline) | 0.1046 |

## EATS Score
**EATS = 0.8211**  
Normalized efficiency penalty: 0.1357  
Accuracy deficit penalty: 0.1200  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 66.67% | 9 |
| LLM-handled (escalated) | 90.91% | 11 |
| Escalation rate | 55.00% | — |