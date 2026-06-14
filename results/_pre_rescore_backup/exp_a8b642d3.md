# Experiment Report — exp_a8b642d3
**Date:** 2026-06-05T21:22:05.584384+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
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
| Accuracy | 72.00% |
| 95% CI | [62.51%, 79.86%] |
| Correct / Total | 72 / 100 |
| Escalation Rate | 42.00% |
| ECE (confidence calibration) | 0.1436 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2531.7 |
| Model avg (ms) | 10191.5 |
| Summed model avg (ms) | 10191.5 |
| Model p50 (ms) | 5384.5 |
| Model p95 (ms) | 32792.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002215 |
| Total cost (USD) | $0.2215 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2215 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0662 |
| Escalated-path total (SLM+LLM) | $0.1553 |
| SLM-path cost fraction | 29.88% |
| Normalized cost (vs baseline) | 0.2732 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.042234 J/tok |
| Total energy (kWh) | 0.021804 |
| Avg energy per sample (kWh) | 0.00021804 |
| Total CO₂ (g) | 8.2857 |
| Avg CO₂ per sample (g) | 0.082857 |
| Normalized energy (vs baseline) | 0.2490 |

## EATS Score
**EATS = 0.5597**  
Normalized efficiency penalty: 0.5664  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 42.00% |
| LLM calls total | 42 |

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 50.00% | 4 |
| college_mathematics | 100.00% | 2 |
| college_medicine | 0.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 100.00% | 4 |
| econometrics | 100.00% | 1 |
| electrical_engineering | 100.00% | 1 |
| elementary_mathematics | 0.00% | 1 |
| formal_logic | 100.00% | 1 |
| global_facts | 0.00% | 2 |
| high_school_chemistry | 100.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_european_history | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 100.00% | 4 |
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
| moral_scenarios | 20.00% | 5 |
| nutrition | 100.00% | 3 |
| philosophy | 50.00% | 2 |
| prehistory | 50.00% | 2 |
| professional_accounting | 66.67% | 3 |
| professional_law | 57.14% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 33.33% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |