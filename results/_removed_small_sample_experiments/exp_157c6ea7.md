# Experiment Report — exp_157c6ea7
**Date:** 2026-06-12T18:21:03.331856+00:00  

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
| Throughput (output tok/s) | 1406.9 |
| Model avg (ms) | 12226.4 |
| Summed model avg (ms) | 12226.4 |
| Model p50 (ms) | 7826.0 |
| Model p95 (ms) | 50863.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002547 |
| Total cost (USD) | $0.1274 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1274 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1274 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3142 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.558872 J/tok |
| Total energy (kWh) | 0.012226 |
| Avg energy per sample (kWh) | 0.00024453 |
| Total CO₂ (g) | 4.6460 |
| Avg CO₂ per sample (g) | 0.092921 |
| Normalized energy (vs baseline) | 0.2793 |

## EATS Score
**EATS = 0.6498**  
Normalized efficiency penalty: 0.5500  
Accuracy deficit penalty: 0.1680  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.