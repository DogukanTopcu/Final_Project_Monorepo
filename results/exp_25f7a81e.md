# Experiment Report — exp_25f7a81e
**Date:** 2026-05-28T19:21:53.161962+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
| SLM | None |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 1000 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 97.00% |
| 95% CI | [0.00%, 0.00%] |
| Correct / Total | 485 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0000 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 0.0 |
| Model avg (ms) | 7768.8 |
| Summed model avg (ms) | 0.0 |
| Model p50 (ms) | 7590.1 |
| Model p95 (ms) | 11791.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000000 |
| Total cost (USD) | $2.5356 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $2.5356 |
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
| Total energy (kWh) | 0.345279 |
| Avg energy per sample (kWh) | 0.00069056 |
| Total CO₂ (g) | 131.2060 |
| Avg CO₂ per sample (g) | 0.262412 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4924**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.