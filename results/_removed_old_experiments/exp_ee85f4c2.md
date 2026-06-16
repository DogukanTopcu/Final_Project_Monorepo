# Experiment Report — exp_ee85f4c2
**Date:** 2026-06-08T20:46:59.333717+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | mmlu |
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
| Escalation Rate | 30.00% |
| ECE (confidence calibration) | 0.0876 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2724.0 |
| Model avg (ms) | 12380.5 |
| Summed model avg (ms) | 12380.5 |
| Model p50 (ms) | 10042.5 |
| Model p95 (ms) | 31941.2 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003439 |
| Total cost (USD) | $0.3439 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3439 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1632 |
| Escalated-path total (SLM+LLM) | $0.1806 |
| SLM-path cost fraction | 47.46% |
| Normalized cost (vs baseline) | 0.4242 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.064933 J/tok |
| Total energy (kWh) | 0.038079 |
| Avg energy per sample (kWh) | 0.00038079 |
| Total CO₂ (g) | 14.4702 |
| Avg CO₂ per sample (g) | 0.144702 |
| Normalized energy (vs baseline) | 0.4349 |

## EATS Score
**EATS = 0.6596**  
Normalized efficiency penalty: 0.6487  
Accuracy deficit penalty: 0.1380  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.