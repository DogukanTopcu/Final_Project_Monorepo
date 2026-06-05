# Experiment Report — exp_faed15c3
**Date:** 2026-06-05T16:37:16.241603+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | speculative |
| Benchmark | arc |
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
| Accuracy | 94.00% |
| 95% CI | [87.52%, 97.22%] |
| Correct / Total | 94 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0971 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2846.0 |
| Model avg (ms) | 1737.2 |
| Summed model avg (ms) | 1737.2 |
| Model p50 (ms) | 1686.9 |
| Model p95 (ms) | 2329.1 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000752 |
| Total cost (USD) | $0.0752 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0752 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0752 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 0.1159 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.929051 J/tok |
| Total energy (kWh) | 0.009516 |
| Avg energy per sample (kWh) | 0.00009516 |
| Total CO₂ (g) | 3.6160 |
| Avg CO₂ per sample (g) | 0.036160 |
| Normalized energy (vs baseline) | 0.1333 |

## EATS Score
**EATS = 0.8516**  
Normalized efficiency penalty: 0.1638  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Speculative Breakdown
| Metric | Value |
|--------|-------|
| Rewrite rate | 100.00% |
| Avg accepted draft ratio | 9.63% |
| Avg draft completion tokens | 20.2 |
| Max draft completion tokens | 64 |
| Avg verifier requests | 2.05 |
| Avg verifier completion tokens | 29.2 |