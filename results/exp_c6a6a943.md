# Experiment Report — exp_c6a6a943
**Date:** 2026-05-28T20:46:52.172705+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
| SLM | None |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 1000 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 90.00% |
| 95% CI | [0.00%, 0.00%] |
| Correct / Total | 9 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0000 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 0.0 |
| Model avg (ms) | 8427.3 |
| Summed model avg (ms) | 0.0 |
| Model p50 (ms) | 8602.6 |
| Model p95 (ms) | 11057.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000000 |
| Total cost (USD) | $0.0550 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0550 |
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
| Total energy (kWh) | 0.007491 |
| Avg energy per sample (kWh) | 0.00074909 |
| Total CO₂ (g) | 2.8466 |
| Avg CO₂ per sample (g) | 0.284656 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.6618**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.0600  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.