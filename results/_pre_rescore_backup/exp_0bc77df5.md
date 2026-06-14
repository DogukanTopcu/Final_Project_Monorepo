# Experiment Report — exp_0bc77df5
**Date:** 2026-05-31T21:31:04.987558+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | gsm8k |
| SLM | None |
| LLM | gemma4-26b-a4b |
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
| Accuracy | 94.80% |
| 95% CI | [92.49%, 96.43%] |
| Correct / Total | 474 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0120 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 33300.1 |
| Wall-clock avg (ms) | 4632.7 |
| Algorithmic avg (ms) | 4632.7 |
| Wall-clock p50 (ms) | 4514.1 |
| Wall-clock p95 (ms) | 6090.4 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003024 |
| Total cost (USD) | $1.5121 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $1.5121 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.5121 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.804795 J/tok |
| Total energy (kWh) | 0.205899 |
| Avg energy per sample (kWh) | 0.00041180 |
| Total CO₂ (g) | 78.2415 |
| Avg CO₂ per sample (g) | 0.156483 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4867**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.