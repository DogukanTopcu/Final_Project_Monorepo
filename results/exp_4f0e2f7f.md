# Experiment Report — exp_4f0e2f7f
**Date:** 2026-05-29T15:45:11.863124+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | humaneval_plus |
| SLM | None |
| LLM | qwen3.5-27b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 3229 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 0.00% |
| 95% CI | [0.00%, 27.75%] |
| Correct / Total | 0 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.8867 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 132.6 |
| Wall-clock avg (ms) | 3915.5 |
| Algorithmic avg (ms) | 3915.5 |
| Wall-clock p50 (ms) | 3944.0 |
| Wall-clock p95 (ms) | 5545.4 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002556 |
| Total cost (USD) | $0.0256 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0256 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0256 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 24.141508 J/tok |
| Total energy (kWh) | 0.003480 |
| Avg energy per sample (kWh) | 0.00034804 |
| Total CO₂ (g) | 1.3226 |
| Avg CO₂ per sample (g) | 0.132255 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.0000**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.