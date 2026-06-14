# Experiment Report — exp_37bd5af4
**Date:** 2026-06-01T06:18:34.580858+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
| SLM | None |
| LLM | qwen3.5-35b-a3b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2034 |
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
| ECE (confidence calibration) | 0.0809 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 56699.3 |
| Model avg (ms) | 2828.7 |
| Summed model avg (ms) | 2828.7 |
| Model p50 (ms) | 2511.5 |
| Model p95 (ms) | 4980.1 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001847 |
| Total cost (USD) | $0.9233 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.9233 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.9233 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.821906 J/tok |
| Total energy (kWh) | 0.125722 |
| Avg energy per sample (kWh) | 0.00025144 |
| Total CO₂ (g) | 47.7744 |
| Avg CO₂ per sample (g) | 0.095549 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6905**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0276  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.