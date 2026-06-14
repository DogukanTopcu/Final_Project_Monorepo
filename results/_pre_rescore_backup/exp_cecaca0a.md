# Experiment Report — exp_cecaca0a
**Date:** 2026-06-13T02:19:56.953187+00:00  

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
| Accuracy | 96.00% |
| 95% CI | [90.16%, 98.43%] |
| Correct / Total | 96 / 100 |
| Escalation Rate | 7.00% |
| ECE (confidence calibration) | 0.1228 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2679.1 |
| Model avg (ms) | 9058.0 |
| Summed model avg (ms) | 9058.0 |
| Model p50 (ms) | 7704.7 |
| Model p95 (ms) | 22669.4 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002049 |
| Total cost (USD) | $0.2049 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2049 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1644 |
| Escalated-path total (SLM+LLM) | $0.0405 |
| SLM-path cost fraction | 80.23% |
| Normalized cost (vs baseline) | 0.2756 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.059281 J/tok |
| Total energy (kWh) | 0.020622 |
| Avg energy per sample (kWh) | 0.00020622 |
| Total CO₂ (g) | 7.8364 |
| Avg CO₂ per sample (g) | 0.078364 |
| Normalized energy (vs baseline) | 0.2638 |

## EATS Score
**EATS = 0.6270**  
Normalized efficiency penalty: 0.5711  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.