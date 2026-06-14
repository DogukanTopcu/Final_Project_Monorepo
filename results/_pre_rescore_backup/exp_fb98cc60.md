# Experiment Report — exp_fb98cc60
**Date:** 2026-06-04T10:14:47.130564+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | truthfulqa |
| SLM | None |
| LLM | None |
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
| Accuracy | 64.00% |
| 95% CI | [54.24%, 72.73%] |
| Correct / Total | 64 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1508 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 3819.7 |
| Wall-clock avg (ms) | 15608.9 |
| Algorithmic avg (ms) | 30680.0 |
| Wall-clock p50 (ms) | 12073.9 |
| Wall-clock p95 (ms) | 44951.8 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006392 |
| Total cost (USD) | $0.6392 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6392 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.6392 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.704942 J/tok |
| Total energy (kWh) | 0.061360 |
| Avg energy per sample (kWh) | 0.00061360 |
| Total CO₂ (g) | 23.3168 |
| Avg CO₂ per sample (g) | 0.233168 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.3902**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 64.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |