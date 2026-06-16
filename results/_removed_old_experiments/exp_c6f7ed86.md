# Experiment Report — exp_c6f7ed86
**Date:** 2026-06-07T18:37:19.192959+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | gsm8k |
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
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 4.00% |
| ECE (confidence calibration) | 0.0363 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2543.3 |
| Model avg (ms) | 14368.0 |
| Summed model avg (ms) | 14368.0 |
| Model p50 (ms) | 11762.5 |
| Model p95 (ms) | 26846.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003167 |
| Total cost (USD) | $0.3167 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.3167 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.2910 |
| Escalated-path total (SLM+LLM) | $0.0258 |
| SLM-path cost fraction | 91.87% |
| Normalized cost (vs baseline) | 0.4261 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.096882 J/tok |
| Total energy (kWh) | 0.031435 |
| Avg energy per sample (kWh) | 0.00031435 |
| Total CO₂ (g) | 11.9453 |
| Avg CO₂ per sample (g) | 0.119453 |
| Normalized energy (vs baseline) | 0.4022 |

## EATS Score
**EATS = 0.7446**  
Normalized efficiency penalty: 0.7397  
Accuracy deficit penalty: 0.0300  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.