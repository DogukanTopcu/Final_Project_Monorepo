# Experiment Report — exp_e8bb4275
**Date:** 2026-06-03T21:13:53.648640+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | mmlu |
| SLM | None |
| LLM | None |
| SLM Temperature | 0.4 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1420 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 59.00% |
| 95% CI | [49.20%, 68.13%] |
| Correct / Total | 59 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.2465 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2157.1 |
| Wall-clock avg (ms) | 26935.5 |
| Algorithmic avg (ms) | 26935.5 |
| Wall-clock p50 (ms) | 24110.4 |
| Wall-clock p95 (ms) | 66524.0 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005612 |
| Total cost (USD) | $0.5612 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5612 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.5612 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.337843 J/tok |
| Total energy (kWh) | 0.053871 |
| Avg energy per sample (kWh) | 0.00053871 |
| Total CO₂ (g) | 20.4710 |
| Avg CO₂ per sample (g) | 0.204710 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.3711**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 59.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 50.00% | 2 |
| clinical_knowledge | 50.00% | 4 |
| college_mathematics | 100.00% | 2 |
| college_medicine | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 75.00% | 4 |
| econometrics | 100.00% | 1 |
| electrical_engineering | 0.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| formal_logic | 0.00% | 1 |
| global_facts | 50.00% | 2 |
| high_school_chemistry | 0.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_european_history | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 50.00% | 4 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_mathematics | 100.00% | 2 |
| high_school_microeconomics | 100.00% | 4 |
| high_school_physics | 50.00% | 2 |
| high_school_statistics | 66.67% | 3 |
| high_school_us_history | 100.00% | 1 |
| high_school_world_history | 50.00% | 4 |
| human_aging | 100.00% | 3 |
| machine_learning | 33.33% | 3 |
| medical_genetics | 100.00% | 1 |
| miscellaneous | 100.00% | 2 |
| moral_disputes | 0.00% | 1 |
| moral_scenarios | 20.00% | 5 |
| nutrition | 66.67% | 3 |
| philosophy | 50.00% | 2 |
| prehistory | 50.00% | 2 |
| professional_accounting | 33.33% | 3 |
| professional_law | 28.57% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 66.67% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |