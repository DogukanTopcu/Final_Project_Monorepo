# Experiment Report — exp_b3cfb2e8
**Date:** 2026-06-02T00:04:23.361381+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | livecodebench |
| SLM | None |
| LLM | gpt-oss-120b |
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
| Accuracy | 9.00% |
| 95% CI | [4.81%, 16.23%] |
| Correct / Total | 9 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.7668 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 14547.1 |
| Wall-clock avg (ms) | 10676.9 |
| Algorithmic avg (ms) | 10676.9 |
| Wall-clock p50 (ms) | 12993.2 |
| Wall-clock p95 (ms) | 13728.0 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.031548 |
| Total cost (USD) | $3.1548 |
| API cost (USD) | $1.2270 |
| Infra cost (USD) | $1.9278 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $1.2270 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $3.1548 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.124523 J/tok |
| Total energy (kWh) | 0.177948 |
| Avg energy per sample (kWh) | 0.00177948 |
| Total CO₂ (g) | 67.6202 |
| Avg CO₂ per sample (g) | 0.676202 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.0826**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Accuracy by Difficulty
| Difficulty | Accuracy | N |
|---|---|---|
| easy | 30.00% | 30 |
| hard | 0.00% | 30 |
| medium | 0.00% | 40 |