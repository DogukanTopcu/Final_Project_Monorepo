# Experiment Report — exp_0fbf27b0
**Date:** 2026-06-07T18:08:14.701027+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 79.00% |
| 95% CI | [70.02%, 85.83%] |
| Correct / Total | 79 / 100 |
| Escalation Rate | 29.00% |
| ECE (confidence calibration) | 0.1088 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2673.4 |
| Model avg (ms) | 23150.7 |
| Summed model avg (ms) | 23150.7 |
| Model p50 (ms) | 16776.3 |
| Model p95 (ms) | 67658.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006337 |
| Total cost (USD) | $0.6337 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6337 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.3783 |
| Escalated-path total (SLM+LLM) | $0.2554 |
| SLM-path cost fraction | 59.70% |
| Normalized cost (vs baseline) | 0.7817 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.058170 J/tok |
| Total energy (kWh) | 0.069767 |
| Avg energy per sample (kWh) | 0.00069767 |
| Total CO₂ (g) | 26.5114 |
| Avg CO₂ per sample (g) | 0.265114 |
| Normalized energy (vs baseline) | 0.7968 |

## EATS Score
**EATS = 0.3586**  
Normalized efficiency penalty: 1.4133  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 50.00% | 4 |
| college_mathematics | 100.00% | 2 |
| college_medicine | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 100.00% | 4 |
| econometrics | 100.00% | 1 |
| electrical_engineering | 100.00% | 1 |
| elementary_mathematics | 0.00% | 1 |
| formal_logic | 100.00% | 1 |
| global_facts | 50.00% | 2 |
| high_school_chemistry | 100.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_european_history | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 75.00% | 4 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_mathematics | 100.00% | 2 |
| high_school_microeconomics | 100.00% | 4 |
| high_school_physics | 50.00% | 2 |
| high_school_statistics | 66.67% | 3 |
| high_school_us_history | 100.00% | 1 |
| high_school_world_history | 75.00% | 4 |
| human_aging | 100.00% | 3 |
| machine_learning | 100.00% | 3 |
| medical_genetics | 100.00% | 1 |
| miscellaneous | 100.00% | 2 |
| moral_disputes | 100.00% | 1 |
| moral_scenarios | 80.00% | 5 |
| nutrition | 100.00% | 3 |
| philosophy | 100.00% | 2 |
| prehistory | 0.00% | 2 |
| professional_accounting | 66.67% | 3 |
| professional_law | 71.43% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 66.67% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |