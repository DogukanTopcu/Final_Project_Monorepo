# Experiment Report — exp_0fcbc737
**Date:** 2026-06-05T18:54:34.451770+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
| Benchmark | arc |
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
| Accuracy | 91.00% |
| 95% CI | [83.77%, 95.19%] |
| Correct / Total | 91 / 100 |
| Escalation Rate | 6.00% |
| ECE (confidence calibration) | 0.0680 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2489.4 |
| Model avg (ms) | 2820.4 |
| Summed model avg (ms) | 2820.4 |
| Model p50 (ms) | 2020.5 |
| Model p95 (ms) | 8380.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000604 |
| Total cost (USD) | $0.0604 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0604 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0490 |
| Escalated-path total (SLM+LLM) | $0.0114 |
| SLM-path cost fraction | 81.09% |
| Normalized cost (vs baseline) | 0.0932 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.026609 J/tok |
| Total energy (kWh) | 0.005903 |
| Avg energy per sample (kWh) | 0.00005903 |
| Total CO₂ (g) | 2.2430 |
| Avg CO₂ per sample (g) | 0.022430 |
| Normalized energy (vs baseline) | 0.0827 |

## EATS Score
**EATS = 0.8857**  
Normalized efficiency penalty: 0.1587  
Accuracy deficit penalty: 0.0540  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 6.00% |
| LLM calls total | 6 |