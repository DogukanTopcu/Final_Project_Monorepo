# Experiment Report — exp_06e26fa4
**Date:** 2026-06-04T16:08:14.841079+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | gsm8k |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1219 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2008.1 |
| Model avg (ms) | 24094.3 |
| Summed model avg (ms) | 20776.9 |
| Model p50 (ms) | 17672.8 |
| Model p95 (ms) | 53312.5 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004329 |
| Total cost (USD) | $0.4329 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.4329 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4329 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.091802 J/tok |
| Total energy (kWh) | 0.041554 |
| Avg energy per sample (kWh) | 0.00041554 |
| Total CO₂ (g) | 15.7905 |
| Avg CO₂ per sample (g) | 0.157905 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6884**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0300  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.