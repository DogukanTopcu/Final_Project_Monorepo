# Experiment Report — exp_5214ebc3
**Date:** 2026-06-04T23:32:26.461872+00:00  

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
| Confidence Threshold | 0.75 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 73.00% |
| 95% CI | [63.57%, 80.73%] |
| Correct / Total | 73 / 100 |
| Escalation Rate | 35.00% |
| ECE (confidence calibration) | 0.0993 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2634.5 |
| Model avg (ms) | 2195.9 |
| Summed model avg (ms) | 2195.9 |
| Model p50 (ms) | 1396.6 |
| Model p95 (ms) | 7802.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000627 |
| Total cost (USD) | $0.0627 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0627 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0290 |
| Escalated-path total (SLM+LLM) | $0.0337 |
| SLM-path cost fraction | 46.24% |
| Normalized cost (vs baseline) | 0.0774 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.371582 J/tok |
| Total energy (kWh) | 0.007025 |
| Avg energy per sample (kWh) | 0.00007025 |
| Total CO₂ (g) | 2.6695 |
| Avg CO₂ per sample (g) | 0.026695 |
| Normalized energy (vs baseline) | 0.0802 |

## EATS Score
**EATS = 0.7776**  
Normalized efficiency penalty: 0.1169  
Accuracy deficit penalty: 0.1620  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 72.31% | 65 |
| LLM-handled (escalated) | 74.29% | 35 |
| Escalation rate | 35.00% | — |