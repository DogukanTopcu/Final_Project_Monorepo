# Experiment Report — exp_f73a0c0a
**Date:** 2026-05-29T15:49:23.078676+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | qwen3.5-27b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 1699 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 90.00% |
| 95% CI | [59.58%, 98.21%] |
| Correct / Total | 9 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.1049 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 241.0 |
| Wall-clock avg (ms) | 19640.0 |
| Algorithmic avg (ms) | 19640.0 |
| Wall-clock p50 (ms) | 17139.9 |
| Wall-clock p95 (ms) | 39831.0 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.012821 |
| Total cost (USD) | $0.1282 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1282 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.1282 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 13.275849 J/tok |
| Total energy (kWh) | 0.017458 |
| Avg energy per sample (kWh) | 0.00174577 |
| Total CO₂ (g) | 6.6339 |
| Avg CO₂ per sample (g) | 0.663394 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4737**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| business_ethics | 100.00% | 1 |
| conceptual_physics | 100.00% | 1 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 50.00% | 2 |