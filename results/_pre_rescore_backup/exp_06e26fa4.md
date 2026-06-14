# Experiment Report — exp_06e26fa4
**Date:** 2026-06-04T16:08:14.818156+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | gsm8k |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1219 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2008.1 |
| Wall-clock avg (ms) | 24094.3 |
| Algorithmic avg (ms) | 20776.9 |
| Wall-clock p50 (ms) | 17672.8 |
| Wall-clock p95 (ms) | 53312.5 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004329 |
| Total cost (USD) | $0.4329 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.4329 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4329 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.091802 J/tok |
| Total energy (kWh) | 0.041554 |
| Avg energy per sample (kWh) | 0.00041554 |
| Total CO₂ (g) | 15.7905 |
| Avg CO₂ per sample (g) | 0.157905 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4872**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.