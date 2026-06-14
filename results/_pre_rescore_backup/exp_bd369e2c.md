# Experiment Report — exp_bd369e2c
**Date:** 2026-06-01T20:28:41.399318+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
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
| Accuracy | 92.00% |
| 95% CI | [85.00%, 95.89%] |
| Correct / Total | 92 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0499 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2112.1 |
| Wall-clock avg (ms) | 8871.7 |
| Algorithmic avg (ms) | 8871.7 |
| Wall-clock p50 (ms) | 8046.9 |
| Wall-clock p95 (ms) | 15220.2 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.016299 |
| Total cost (USD) | $1.6299 |
| API cost (USD) | $0.0281 |
| Infra cost (USD) | $1.6018 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0281 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.6299 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 28.407770 J/tok |
| Total energy (kWh) | 0.147862 |
| Avg energy per sample (kWh) | 0.00147862 |
| Total CO₂ (g) | 56.1877 |
| Avg CO₂ per sample (g) | 0.561877 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4792**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.