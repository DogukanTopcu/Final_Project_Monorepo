# Experiment Report — exp_9d9638fd
**Date:** 2026-06-02T23:05:51.481823+00:00  

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
| Accuracy | 74.00% |
| 95% CI | [64.63%, 81.60%] |
| Correct / Total | 74 / 100 |
| Escalation Rate | 15.00% |
| ECE (confidence calibration) | 0.1630 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2218.1 |
| Wall-clock avg (ms) | 30636.2 |
| Algorithmic avg (ms) | 30636.2 |
| Wall-clock p50 (ms) | 25293.1 |
| Wall-clock p95 (ms) | 64346.6 |

> **Wall-clock**: observed end-to-end time including network and queue.  
> **Algorithmic**: intrinsic inference + orchestration time summed across steps.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006594 |
| Total cost (USD) | $0.6594 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6594 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4486 |
| Escalated-path total (SLM+LLM) | $0.2108 |
| SLM-path cost fraction | 68.03% |
| Normalized cost (vs baseline) | 1.0539 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.419709 J/tok |
| Total energy (kWh) | 0.064550 |
| Avg energy per sample (kWh) | 0.00064550 |
| Total CO₂ (g) | 24.5289 |
| Avg CO₂ per sample (g) | 0.245289 |
| Normalized energy (vs baseline) | 0.7577 |

## EATS Score
**EATS = 0.3113**  
Normalized efficiency penalty: 1.6374  

> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  
> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 15.00% |
| LLM calls total | 15 |

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
| moral_disputes | 0.00% | 1 |
| moral_scenarios | 40.00% | 5 |
| nutrition | 100.00% | 3 |
| philosophy | 100.00% | 2 |
| prehistory | 50.00% | 2 |
| professional_accounting | 66.67% | 3 |
| professional_law | 50.00% | 14 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 50.00% | 2 |
| security_studies | 33.33% | 3 |
| sociology | 100.00% | 1 |
| us_foreign_policy | 100.00% | 1 |
| world_religions | 100.00% | 2 |