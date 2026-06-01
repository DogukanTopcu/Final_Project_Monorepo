# Experiment Report — exp_befdc2c0
**Date:** 2026-05-31T20:49:36.536491+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | arc |
| SLM | None |
| LLM | gemma4-26b-a4b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2007 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 95.40% |
| 95% CI | [93.19%, 96.92%] |
| Correct / Total | 477 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0413 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 17540.4 |
| Wall-clock avg (ms) | 7386.6 |
| Algorithmic avg (ms) | 7386.6 |
| Wall-clock p50 (ms) | 7150.0 |
| Wall-clock p95 (ms) | 9959.6 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004822 |
| Total cost (USD) | $2.4109 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $2.4109 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $2.4109 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 9.121779 J/tok |
| Total energy (kWh) | 0.328295 |
| Avg energy per sample (kWh) | 0.00065659 |
| Total CO₂ (g) | 124.7522 |
| Avg CO₂ per sample (g) | 0.249504 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4882**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.