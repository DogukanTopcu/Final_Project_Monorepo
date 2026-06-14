# Experiment Report — exp_b8cf2ca6
**Date:** 2026-06-05T16:52:03.395598+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | speculative |
| Benchmark | hellaswag |
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
| Accuracy | 92.00% |
| 95% CI | [85.00%, 95.89%] |
| Correct / Total | 92 / 100 |
| Escalation Rate | 89.00% |
| ECE (confidence calibration) | 0.1339 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2775.2 |
| Model avg (ms) | 1734.3 |
| Summed model avg (ms) | 1734.3 |
| Model p50 (ms) | 1711.3 |
| Model p95 (ms) | 2292.4 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000720 |
| Total cost (USD) | $0.0720 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0720 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0038 |
| Escalated-path total (SLM+LLM) | $0.0682 |
| SLM-path cost fraction | 5.29% |
| Normalized cost (vs baseline) | 0.1064 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.750956 J/tok |
| Total energy (kWh) | 0.009026 |
| Avg energy per sample (kWh) | 0.00009026 |
| Total CO₂ (g) | 3.4297 |
| Avg CO₂ per sample (g) | 0.034297 |
| Normalized energy (vs baseline) | 0.1246 |

## EATS Score
**EATS = 0.8988**  
Normalized efficiency penalty: 0.1390  
Accuracy deficit penalty: 0.0480  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Speculative Breakdown
| Metric | Value |
|--------|-------|
| Rewrite rate | 89.00% |
| Avg accepted draft ratio | 18.24% |
| Avg draft completion tokens | 21.6 |
| Max draft completion tokens | 64 |
| Avg verifier requests | 1.90 |
| Avg verifier completion tokens | 26.5 |