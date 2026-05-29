# Experiment Report — exp_ac21ba45
**Date:** 2026-05-29T14:23:07.409052+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
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
| Accuracy | 59.40% |
| 95% CI | [55.04%, 63.62%] |
| Correct / Total | 297 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.1660 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 57881.7 |
| Wall-clock avg (ms) | 3943.7 |
| Algorithmic avg (ms) | 3943.7 |
| Wall-clock p50 (ms) | 3551.0 |
| Wall-clock p95 (ms) | 6497.9 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003364 |
| Total cost (USD) | $1.6822 |
| API cost (USD) | $0.3950 |
| Infra cost (USD) | $1.2872 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.3950 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.6822 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.764259 J/tok |
| Total energy (kWh) | 0.175276 |
| Avg energy per sample (kWh) | 0.00035055 |
| Total CO₂ (g) | 66.6047 |
| Avg CO₂ per sample (g) | 0.133209 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.3726**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.