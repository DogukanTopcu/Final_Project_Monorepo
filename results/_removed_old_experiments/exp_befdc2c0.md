# Experiment Report — exp_befdc2c0
**Date:** 2026-05-31T20:49:36.536491+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
| SLM | None |
| LLM | gemma4-26b-a4b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2007 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 95.40% |
| 95% CI | [93.19%, 96.92%] |
| Correct / Total | 477 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0413 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 17540.4 |
| Model avg (ms) | 7386.6 |
| Summed model avg (ms) | 7386.6 |
| Model p50 (ms) | 7150.0 |
| Model p95 (ms) | 9959.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004822 |
| Total cost (USD) | $2.4109 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $2.4109 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $2.4109 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 9.121779 J/tok |
| Total energy (kWh) | 0.328295 |
| Avg energy per sample (kWh) | 0.00065659 |
| Total CO₂ (g) | 124.7522 |
| Avg CO₂ per sample (g) | 0.249504 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6905**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0276  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.