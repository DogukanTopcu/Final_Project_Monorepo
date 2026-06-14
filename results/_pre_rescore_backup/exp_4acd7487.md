# Experiment Report — exp_4acd7487
**Date:** 2026-05-29T19:04:33.113228+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
| SLM | None |
| LLM | qwen3.5-27b |
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
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0519 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2293.2 |
| Wall-clock avg (ms) | 13859.6 |
| Algorithmic avg (ms) | 13859.6 |
| Wall-clock p50 (ms) | 12572.7 |
| Wall-clock p95 (ms) | 23563.8 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.009047 |
| Total cost (USD) | $0.9047 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.9047 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.9047 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 13.954223 J/tok |
| Total energy (kWh) | 0.123196 |
| Avg energy per sample (kWh) | 0.00123196 |
| Total CO₂ (g) | 46.8146 |
| Avg CO₂ per sample (g) | 0.468146 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4872**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.