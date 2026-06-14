# Experiment Report — exp_ccf80089
**Date:** 2026-06-06T21:35:49.684798+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | multi_agent |
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
| Accuracy | 69.00% |
| 95% CI | [59.37%, 77.22%] |
| Correct / Total | 69 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1600 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2525.5 |
| Model avg (ms) | 25560.2 |
| Summed model avg (ms) | 25560.2 |
| Model p50 (ms) | 23838.7 |
| Model p95 (ms) | 57635.8 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005325 |
| Total cost (USD) | $0.5325 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5325 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.5325 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.8511 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.850893 J/tok |
| Total energy (kWh) | 0.051120 |
| Avg energy per sample (kWh) | 0.00051120 |
| Total CO₂ (g) | 19.4258 |
| Avg CO₂ per sample (g) | 0.194258 |
| Normalized energy (vs baseline) | 0.6000 |

## EATS Score
**EATS = 0.3390**  
Normalized efficiency penalty: 1.3456  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | slm |
| LLM arbitration rate | 0.00% |

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 50.00% | 4 |
| college_mathematics | 50.00% | 2 |
| college_medicine | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 75.00% | 4 |
| econometrics | 100.00% | 1 |
| electrical_engineering | 100.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| formal_logic | 100.00% | 1 |
| global_facts | 0.00% | 2 |
| high_school_chemistry | 100.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_european_history | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 75.00% | 4 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_mathematics | 100.00% | 2 |
| high_school_microeconomics | 100.00% | 4 |
| high_school_physics | 50.00% | 2 |
| high_school_statistics | 100.00% | 3 |
| high_school_us_history | 100.00% | 1 |
| high_school_world_history | 75.00% | 4 |
| human_aging | 100.00% | 3 |
| machine_learning | 33.33% | 3 |
| medical_genetics | 100.00% | 1 |
| miscellaneous | 100.00% | 2 |
| moral_disputes | 100.00% | 1 |
| moral_scenarios | 40.00% | 5 |
| nutrition | 66.67% | 3 |
| philosophy | 50.00% | 2 |
| prehistory | 50.00% | 2 |
| professional_accounting | 66.67% | 3 |
| professional_law | 50.00% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 33.33% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |