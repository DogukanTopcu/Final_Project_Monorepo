# Experiment Report — exp_3a953bad
**Date:** 2026-05-28T14:01:37.198834+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 60.00% |
| 95% CI | [0.00%, 0.00%] |
| Correct / Total | 6 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0000 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 0.0 |
| Model avg (ms) | 8496.3 |
| Summed model avg (ms) | 0.0 |
| Model p50 (ms) | 9036.8 |
| Model p95 (ms) | 10250.4 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000000 |
| Total cost (USD) | $0.0555 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0555 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 0.000000 J/tok |
| Total energy (kWh) | 0.007552 |
| Avg energy per sample (kWh) | 0.00075522 |
| Total CO₂ (g) | 2.8699 |
| Avg CO₂ per sample (g) | 0.286985 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.3750**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.