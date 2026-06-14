# Experiment Report — exp_06cb6a22
**Date:** 2026-06-04T23:59:20.604869+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.8 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 77.00% |
| 95% CI | [67.85%, 84.16%] |
| Correct / Total | 77 / 100 |
| Escalation Rate | 56.00% |
| ECE (confidence calibration) | 0.0968 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2726.5 |
| Model avg (ms) | 2473.5 |
| Summed model avg (ms) | 2473.5 |
| Model p50 (ms) | 1551.5 |
| Model p95 (ms) | 7799.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.000805 |
| Total cost (USD) | $0.0805 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0805 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0177 |
| Escalated-path total (SLM+LLM) | $0.0628 |
| SLM-path cost fraction | 21.95% |
| Normalized cost (vs baseline) | 0.0993 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.036282 J/tok |
| Total energy (kWh) | 0.009435 |
| Avg energy per sample (kWh) | 0.00009435 |
| Total CO₂ (g) | 3.5852 |
| Avg CO₂ per sample (g) | 0.035852 |
| Normalized energy (vs baseline) | 0.1077 |

## EATS Score
**EATS = 0.8249**  
Normalized efficiency penalty: 0.1634  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Routing Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| SLM-handled (no escalation) | 75.00% | 44 |
| LLM-handled (escalated) | 78.57% | 56 |
| Escalation rate | 56.00% | — |

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 75.00% | 4 |
| college_mathematics | 50.00% | 2 |
| college_medicine | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 100.00% | 4 |
| econometrics | 100.00% | 1 |
| electrical_engineering | 100.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| formal_logic | 100.00% | 1 |
| global_facts | 100.00% | 2 |
| high_school_chemistry | 100.00% | 1 |
| high_school_computer_science | 0.00% | 1 |
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
| moral_scenarios | 40.00% | 5 |
| nutrition | 100.00% | 3 |
| philosophy | 50.00% | 2 |
| prehistory | 50.00% | 2 |
| professional_accounting | 33.33% | 3 |
| professional_law | 78.57% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 33.33% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |