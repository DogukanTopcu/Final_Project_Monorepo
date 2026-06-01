# Experiment Report — exp_f164f3df
**Date:** 2026-06-01T09:06:03.479361+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
| SLM | None |
| LLM | qwen3.5-35b-a3b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2011 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 95.60% |
| 95% CI | [93.43%, 97.08%] |
| Correct / Total | 478 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0131 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 38930.5 |
| Wall-clock avg (ms) | 4510.5 |
| Algorithmic avg (ms) | 4510.5 |
| Wall-clock p50 (ms) | 4249.6 |
| Wall-clock p95 (ms) | 6242.3 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002944 |
| Total cost (USD) | $1.4722 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $1.4722 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.4722 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.109885 J/tok |
| Total energy (kWh) | 0.200465 |
| Avg energy per sample (kWh) | 0.00040093 |
| Total CO₂ (g) | 76.1768 |
| Avg CO₂ per sample (g) | 0.152354 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4888**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.