# Experiment Report — exp_f49f827d
**Date:** 2026-06-02T23:51:09.598050+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
| Benchmark | arc |
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
| Accuracy | 91.00% |
| 95% CI | [83.77%, 95.19%] |
| Correct / Total | 91 / 100 |
| Escalation Rate | 3.00% |
| ECE (confidence calibration) | 0.0644 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2197.5 |
| Wall-clock avg (ms) | 21429.0 |
| Algorithmic avg (ms) | 21429.0 |
| Wall-clock p50 (ms) | 18225.4 |
| Wall-clock p95 (ms) | 35397.9 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004512 |
| Total cost (USD) | $0.4512 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.4512 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.3922 |
| Escalated-path total (SLM+LLM) | $0.0590 |
| SLM-path cost fraction | 86.93% |
| Normalized cost (vs baseline) | 0.8896 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.332340 J/tok |
| Total energy (kWh) | 0.043590 |
| Avg energy per sample (kWh) | 0.00043590 |
| Total CO₂ (g) | 16.5641 |
| Avg CO₂ per sample (g) | 0.165641 |
| Normalized energy (vs baseline) | 0.6312 |

## EATS Score
**EATS = 0.3942**  
Normalized efficiency penalty: 1.3986  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 3.00% |
| LLM calls total | 3 |