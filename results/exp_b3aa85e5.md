# Experiment Report — exp_b3aa85e5
**Date:** 2026-06-09T22:56:34.477025+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
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
| Accuracy | 77.00% |
| 95% CI | [67.85%, 84.16%] |
| Correct / Total | 77 / 100 |
| Escalation Rate | 41.00% |
| ECE (confidence calibration) | 0.0382 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2838.1 |
| Model avg (ms) | 8457.1 |
| Summed model avg (ms) | 8457.1 |
| Model p50 (ms) | 7513.0 |
| Model p95 (ms) | 16163.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002865 |
| Total cost (USD) | $0.2865 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2865 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1121 |
| Escalated-path total (SLM+LLM) | $0.1744 |
| SLM-path cost fraction | 39.11% |
| Normalized cost (vs baseline) | 0.4234 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.101401 J/tok |
| Total energy (kWh) | 0.034012 |
| Avg energy per sample (kWh) | 0.00034012 |
| Total CO₂ (g) | 12.9246 |
| Avg CO₂ per sample (g) | 0.129246 |
| Normalized energy (vs baseline) | 0.4694 |

## EATS Score
**EATS = 0.6719**  
Normalized efficiency penalty: 0.5952  
Accuracy deficit penalty: 0.1380  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.