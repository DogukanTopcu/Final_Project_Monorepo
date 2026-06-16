# Experiment Report — exp_3e6e079a
**Date:** 2026-05-29T18:32:20.950798+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | qwen3.5-27b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 87.20% |
| 95% CI | [83.99%, 89.85%] |
| Correct / Total | 436 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0589 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 12017.8 |
| Model avg (ms) | 19276.9 |
| Summed model avg (ms) | 19276.9 |
| Model p50 (ms) | 15849.3 |
| Model p95 (ms) | 43325.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.012584 |
| Total cost (USD) | $6.2918 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $6.2918 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $6.2918 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 13.313632 J/tok |
| Total energy (kWh) | 0.856751 |
| Avg energy per sample (kWh) | 0.00171350 |
| Total CO₂ (g) | 325.5653 |
| Avg CO₂ per sample (g) | 0.651131 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6465**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0768  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.