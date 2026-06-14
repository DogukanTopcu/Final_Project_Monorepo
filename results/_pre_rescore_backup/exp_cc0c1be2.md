# Experiment Report — exp_cc0c1be2
**Date:** 2026-06-01T20:41:12.642686+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | hellaswag |
| SLM | None |
| LLM | llama3.3-70b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 89.00% |
| 95% CI | [81.37%, 93.75%] |
| Correct / Total | 89 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0574 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1999.2 |
| Wall-clock avg (ms) | 7446.3 |
| Algorithmic avg (ms) | 7446.3 |
| Wall-clock p50 (ms) | 6128.2 |
| Wall-clock p95 (ms) | 13632.5 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.013800 |
| Total cost (USD) | $1.3800 |
| API cost (USD) | $0.0355 |
| Infra cost (USD) | $1.3445 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0355 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.3800 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 30.011390 J/tok |
| Total energy (kWh) | 0.124105 |
| Avg energy per sample (kWh) | 0.00124105 |
| Total CO₂ (g) | 47.1601 |
| Avg CO₂ per sample (g) | 0.471601 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4709**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.