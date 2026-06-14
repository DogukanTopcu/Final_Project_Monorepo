# Experiment Report — exp_8e6d351b
**Date:** 2026-06-12T19:02:58.757359+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 50 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 72.00% |
| 95% CI | [58.33%, 82.53%] |
| Correct / Total | 36 / 50 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1361 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1406.7 |
| Model avg (ms) | 12228.3 |
| Summed model avg (ms) | 12228.3 |
| Model p50 (ms) | 7830.3 |
| Model p95 (ms) | 50878.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002548 |
| Total cost (USD) | $0.1274 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1274 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1274 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3143 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.559258 J/tok |
| Total energy (kWh) | 0.012228 |
| Avg energy per sample (kWh) | 0.00024457 |
| Total CO₂ (g) | 4.6467 |
| Avg CO₂ per sample (g) | 0.092935 |
| Normalized energy (vs baseline) | 0.2793 |

## EATS Score
**EATS = 0.6498**  
Normalized efficiency penalty: 0.5501  
Accuracy deficit penalty: 0.1680  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.