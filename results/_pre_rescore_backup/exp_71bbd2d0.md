# Experiment Report — exp_71bbd2d0
**Date:** 2026-06-04T09:48:34.400465+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | gsm8k |
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
| Accuracy | 96.00% |
| 95% CI | [90.16%, 98.43%] |
| Correct / Total | 96 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0602 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 6936.3 |
| Wall-clock avg (ms) | 16147.3 |
| Algorithmic avg (ms) | 43770.8 |
| Wall-clock p50 (ms) | 14513.9 |
| Wall-clock p95 (ms) | 29501.5 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.009119 |
| Total cost (USD) | $0.9119 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.9119 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.9119 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.813784 J/tok |
| Total energy (kWh) | 0.087542 |
| Avg energy per sample (kWh) | 0.00087542 |
| Total CO₂ (g) | 33.2658 |
| Avg CO₂ per sample (g) | 0.332658 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4898**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 96.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |