# Experiment Report — exp_79d1fada
**Date:** 2026-05-29T13:27:36.888649+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | hellaswag |
| SLM | None |
| LLM | gpt-oss-20b |
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
| Accuracy | 78.00% |
| 95% CI | [74.16%, 81.41%] |
| Correct / Total | 390 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0243 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 55257.4 |
| Wall-clock avg (ms) | 3789.8 |
| Algorithmic avg (ms) | 3789.8 |
| Wall-clock p50 (ms) | 3610.4 |
| Wall-clock p95 (ms) | 5184.5 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003252 |
| Total cost (USD) | $1.6261 |
| API cost (USD) | $0.3891 |
| Infra cost (USD) | $1.2369 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.3891 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.6261 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.895541 J/tok |
| Total energy (kWh) | 0.168434 |
| Avg energy per sample (kWh) | 0.00033687 |
| Total CO₂ (g) | 64.0048 |
| Avg CO₂ per sample (g) | 0.128010 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4382**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.