# Experiment Report — exp_085e1b0a
**Date:** 2026-05-29T12:29:34.694393+00:00  

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
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 79.80% |
| 95% CI | [76.06%, 83.09%] |
| Correct / Total | 399 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0681 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 52611.8 |
| Wall-clock avg (ms) | 3544.9 |
| Algorithmic avg (ms) | 3544.9 |
| Wall-clock p50 (ms) | 2884.6 |
| Wall-clock p95 (ms) | 9901.6 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002990 |
| Total cost (USD) | $1.4949 |
| API cost (USD) | $0.3379 |
| Infra cost (USD) | $1.1570 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.3379 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $1.4949 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.041142 J/tok |
| Total energy (kWh) | 0.157550 |
| Avg energy per sample (kWh) | 0.00031510 |
| Total CO₂ (g) | 59.8689 |
| Avg CO₂ per sample (g) | 0.119738 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4438**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| abstract_algebra | 75.00% | 4 |
| anatomy | 100.00% | 6 |
| astronomy | 100.00% | 3 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 62.50% | 8 |
| college_biology | 100.00% | 5 |
| college_chemistry | 87.50% | 8 |
| college_computer_science | 75.00% | 4 |
| college_mathematics | 80.00% | 10 |
| college_medicine | 87.50% | 8 |
| college_physics | 100.00% | 2 |
| computer_security | 100.00% | 6 |
| conceptual_physics | 100.00% | 13 |
| econometrics | 100.00% | 5 |
| electrical_engineering | 100.00% | 4 |
| elementary_mathematics | 91.67% | 12 |
| formal_logic | 75.00% | 4 |
| global_facts | 37.50% | 8 |
| high_school_biology | 83.33% | 6 |
| high_school_chemistry | 85.71% | 7 |
| high_school_computer_science | 100.00% | 2 |
| high_school_european_history | 75.00% | 4 |
| high_school_geography | 71.43% | 14 |
| high_school_government_and_politics | 87.50% | 8 |
| high_school_macroeconomics | 88.24% | 17 |
| high_school_mathematics | 93.33% | 15 |
| high_school_microeconomics | 100.00% | 10 |
| high_school_physics | 75.00% | 4 |
| high_school_psychology | 86.67% | 15 |
| high_school_statistics | 75.00% | 8 |
| high_school_us_history | 100.00% | 3 |
| high_school_world_history | 71.43% | 7 |
| human_aging | 88.89% | 9 |
| human_sexuality | 100.00% | 1 |
| international_law | 75.00% | 4 |
| jurisprudence | 100.00% | 6 |
| logical_fallacies | 100.00% | 1 |
| machine_learning | 75.00% | 8 |
| management | 50.00% | 2 |
| marketing | 100.00% | 6 |
| medical_genetics | 100.00% | 2 |
| miscellaneous | 95.83% | 24 |
| moral_disputes | 63.64% | 11 |
| moral_scenarios | 80.00% | 40 |
| nutrition | 91.67% | 12 |
| philosophy | 75.00% | 12 |
| prehistory | 71.43% | 7 |
| professional_accounting | 69.23% | 13 |
| professional_law | 47.46% | 59 |
| professional_medicine | 100.00% | 9 |
| professional_psychology | 81.25% | 16 |
| public_relations | 100.00% | 1 |
| security_studies | 66.67% | 9 |
| sociology | 50.00% | 2 |
| us_foreign_policy | 100.00% | 4 |
| virology | 100.00% | 3 |
| world_religions | 85.71% | 7 |