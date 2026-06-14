# Experiment Report — exp_a952b38f
**Date:** 2026-05-29T11:58:01.462123+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | gpt-oss-20b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2001 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 100.00% |
| 95% CI | [72.25%, 100.00%] |
| Correct / Total | 10 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.2367 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1028.5 |
| Model avg (ms) | 3516.8 |
| Summed model avg (ms) | 3516.8 |
| Model p50 (ms) | 3274.3 |
| Model p95 (ms) | 6712.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002953 |
| Total cost (USD) | $0.0295 |
| API cost (USD) | $0.0066 |
| Infra cost (USD) | $0.0230 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0066 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0295 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.111328 J/tok |
| Total energy (kWh) | 0.003126 |
| Avg energy per sample (kWh) | 0.00031260 |
| Total CO₂ (g) | 1.1879 |
| Avg CO₂ per sample (g) | 0.118789 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.7143**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0000  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.