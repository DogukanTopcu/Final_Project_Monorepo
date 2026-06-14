# Experiment Report — exp_5c0dacaf
**Date:** 2026-06-12T19:42:05.465229+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 50 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 70.00% |
| 95% CI | [56.25%, 80.90%] |
| Correct / Total | 35 / 50 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1723 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1328.8 |
| Model avg (ms) | 14967.3 |
| Summed model avg (ms) | 14967.3 |
| Model p50 (ms) | 8513.3 |
| Model p95 (ms) | 50889.9 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003118 |
| Total cost (USD) | $0.1559 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1559 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1559 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3846 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.709295 J/tok |
| Total energy (kWh) | 0.014967 |
| Avg energy per sample (kWh) | 0.00029935 |
| Total CO₂ (g) | 5.6876 |
| Avg CO₂ per sample (g) | 0.113752 |
| Normalized energy (vs baseline) | 0.3419 |

## EATS Score
**EATS = 0.4609**  
Normalized efficiency penalty: 0.8187  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| anatomy | 100.00% | 1 |
| business_ethics | 100.00% | 2 |
| clinical_knowledge | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 2 |
| conceptual_physics | 100.00% | 2 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 0.00% | 1 |
| formal_logic | 100.00% | 1 |
| global_facts | 100.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 50.00% | 2 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 3 |
| high_school_statistics | 50.00% | 2 |
| machine_learning | 100.00% | 3 |
| medical_genetics | 100.00% | 1 |
| moral_disputes | 0.00% | 1 |
| moral_scenarios | 33.33% | 3 |
| nutrition | 100.00% | 2 |
| philosophy | 0.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 62.50% | 8 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 0.00% | 1 |
| security_studies | 50.00% | 2 |