# Experiment Report — exp_c6de056b
**Date:** 2026-05-29T12:53:07.696913+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
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
| Accuracy | 93.80% |
| 95% CI | [91.33%, 95.60%] |
| Correct / Total | 469 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.2065 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 33071.5 |
| Wall-clock avg (ms) | 2691.1 |
| Algorithmic avg (ms) | 2691.1 |
| Wall-clock p50 (ms) | 2482.4 |
| Wall-clock p95 (ms) | 3800.4 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002104 |
| Total cost (USD) | $1.0522 |
| API cost (USD) | $0.1739 |
| Infra cost (USD) | $0.8783 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.1739 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.0522 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.838009 J/tok |
| Total energy (kWh) | 0.119602 |
| Avg energy per sample (kWh) | 0.00023920 |
| Total CO₂ (g) | 45.4489 |
| Avg CO₂ per sample (g) | 0.090898 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4840**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.