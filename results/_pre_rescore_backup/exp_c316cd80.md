# Experiment Report — exp_c316cd80
**Date:** 2026-05-29T15:13:00.153269+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | humaneval_plus |
| SLM | None |
| LLM | gpt-oss-20b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 3825 |
| SLM Only | False |
| N Samples | 20 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 10.00% |
| 95% CI | [2.79%, 30.10%] |
| Correct / Total | 2 / 20 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.7057 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2162.1 |
| Wall-clock avg (ms) | 3821.4 |
| Algorithmic avg (ms) | 3821.4 |
| Wall-clock p50 (ms) | 3355.5 |
| Wall-clock p95 (ms) | 11955.8 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003241 |
| Total cost (USD) | $0.0648 |
| API cost (USD) | $0.0149 |
| Infra cost (USD) | $0.0499 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0149 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0648 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.960146 J/tok |
| Total energy (kWh) | 0.006794 |
| Avg energy per sample (kWh) | 0.00033968 |
| Total CO₂ (g) | 2.5815 |
| Avg CO₂ per sample (g) | 0.129077 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.0909**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.