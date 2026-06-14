# Experiment Report — exp_e1e366df
**Date:** 2026-06-03T01:13:41.974143+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
| Benchmark | hellaswag |
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
| Accuracy | 66.00% |
| 95% CI | [56.28%, 74.54%] |
| Correct / Total | 66 / 100 |
| Escalation Rate | 1.00% |
| ECE (confidence calibration) | 0.1921 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2244.3 |
| Wall-clock avg (ms) | 24323.2 |
| Algorithmic avg (ms) | 24323.2 |
| Wall-clock p50 (ms) | 24067.4 |
| Wall-clock p95 (ms) | 36206.3 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005077 |
| Total cost (USD) | $0.5077 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5077 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4923 |
| Escalated-path total (SLM+LLM) | $0.0154 |
| SLM-path cost fraction | 96.96% |
| Normalized cost (vs baseline) | 1.1324 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.218303 J/tok |
| Total energy (kWh) | 0.048801 |
| Avg energy per sample (kWh) | 0.00048801 |
| Total CO₂ (g) | 18.5444 |
| Avg CO₂ per sample (g) | 0.185444 |
| Normalized energy (vs baseline) | 0.7993 |

## EATS Score
**EATS = 0.2696**  
Normalized efficiency penalty: 1.7884  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 1.00% |
| LLM calls total | 1 |