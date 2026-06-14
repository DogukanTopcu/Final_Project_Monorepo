# Experiment Report — exp_a952b38f
**Date:** 2026-05-29T11:58:01.462123+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | monolithic |
| Benchmark | mmlu |
| SLM | None |
| LLM | gpt-oss-20b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 2001 |
| SLM Only | False |
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 100.00% |
| 95% CI | [72.25%, 100.00%] |
| Correct / Total | 10 / 10 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.2367 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1028.5 |
| Wall-clock avg (ms) | 3516.8 |
| Algorithmic avg (ms) | 3516.8 |
| Wall-clock p50 (ms) | 3274.3 |
| Wall-clock p95 (ms) | 6712.6 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002953 |
| Total cost (USD) | $0.0295 |
| API cost (USD) | $0.0066 |
| Infra cost (USD) | $0.0230 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0066 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.0295 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.111328 J/tok |
| Total energy (kWh) | 0.003126 |
| Avg energy per sample (kWh) | 0.00031260 |
| Total CO₂ (g) | 1.1879 |
| Avg CO₂ per sample (g) | 0.118789 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.5000**  
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
| professional_law | 100.00% | 2 |