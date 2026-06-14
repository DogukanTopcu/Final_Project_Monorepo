# Experiment Report — exp_f73a0c0a
**Date:** 2026-05-29T15:49:23.078676+00:00  

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
| LLM Max Tokens | 1699 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 90.00% |
| 95% CI | [59.58%, 98.21%] |
| Correct / Total | 9 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.1049 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 241.0 |
| Model avg (ms) | 19640.0 |
| Summed model avg (ms) | 19640.0 |
| Model p50 (ms) | 17139.9 |
| Model p95 (ms) | 39831.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.012821 |
| Total cost (USD) | $0.1282 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1282 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.1282 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 13.275849 J/tok |
| Total energy (kWh) | 0.017458 |
| Avg energy per sample (kWh) | 0.00174577 |
| Total CO₂ (g) | 6.6339 |
| Avg CO₂ per sample (g) | 0.663394 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6618**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0600  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.