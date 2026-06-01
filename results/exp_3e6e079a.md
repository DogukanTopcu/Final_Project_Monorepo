# Experiment Report — exp_3e6e079a
**Date:** 2026-05-29T18:32:20.950798+00:00  

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
| LLM Max Tokens | 2000 |
| SLM Only | False |
| N Samples | 500 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 87.20% |
| 95% CI | [83.99%, 89.85%] |
| Correct / Total | 436 / 500 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0589 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 12017.8 |
| Wall-clock avg (ms) | 19276.9 |
| Algorithmic avg (ms) | 19276.9 |
| Wall-clock p50 (ms) | 15849.3 |
| Wall-clock p95 (ms) | 43325.0 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.012584 |
| Total cost (USD) | $6.2918 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $6.2918 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $6.2918 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 13.313632 J/tok |
| Total energy (kWh) | 0.856751 |
| Avg energy per sample (kWh) | 0.00171350 |
| Total CO₂ (g) | 325.5653 |
| Avg CO₂ per sample (g) | 0.651131 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4658**  
Normalized efficiency penalty: 1.0000  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| abstract_algebra | 100.00% | 4 |
| anatomy | 100.00% | 6 |
| astronomy | 100.00% | 3 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 87.50% | 8 |
| college_biology | 100.00% | 5 |
| college_chemistry | 87.50% | 8 |
| college_computer_science | 100.00% | 4 |
| college_mathematics | 100.00% | 10 |
| college_medicine | 87.50% | 8 |
| college_physics | 100.00% | 2 |
| computer_security | 100.00% | 6 |
| conceptual_physics | 100.00% | 13 |
| econometrics | 100.00% | 5 |
| electrical_engineering | 100.00% | 4 |
| elementary_mathematics | 100.00% | 12 |
| formal_logic | 75.00% | 4 |
| global_facts | 62.50% | 8 |
| high_school_biology | 66.67% | 6 |
| high_school_chemistry | 100.00% | 7 |
| high_school_computer_science | 100.00% | 2 |
| high_school_european_history | 75.00% | 4 |
| high_school_geography | 71.43% | 14 |
| high_school_government_and_politics | 100.00% | 8 |
| high_school_macroeconomics | 94.12% | 17 |
| high_school_mathematics | 100.00% | 15 |
| high_school_microeconomics | 100.00% | 10 |
| high_school_physics | 75.00% | 4 |
| high_school_psychology | 93.33% | 15 |
| high_school_statistics | 87.50% | 8 |
| high_school_us_history | 100.00% | 3 |
| high_school_world_history | 85.71% | 7 |
| human_aging | 100.00% | 9 |
| human_sexuality | 0.00% | 1 |
| international_law | 100.00% | 4 |
| jurisprudence | 100.00% | 6 |
| logical_fallacies | 100.00% | 1 |
| machine_learning | 100.00% | 8 |
| management | 50.00% | 2 |
| marketing | 66.67% | 6 |
| medical_genetics | 100.00% | 2 |
| miscellaneous | 100.00% | 24 |
| moral_disputes | 81.82% | 11 |
| moral_scenarios | 77.50% | 40 |
| nutrition | 91.67% | 12 |
| philosophy | 83.33% | 12 |
| prehistory | 71.43% | 7 |
| professional_accounting | 100.00% | 13 |
| professional_law | 72.88% | 59 |
| professional_medicine | 100.00% | 9 |
| professional_psychology | 81.25% | 16 |
| public_relations | 100.00% | 1 |
| security_studies | 55.56% | 9 |
| sociology | 100.00% | 2 |
| us_foreign_policy | 100.00% | 4 |
| virology | 66.67% | 3 |
| world_religions | 85.71% | 7 |