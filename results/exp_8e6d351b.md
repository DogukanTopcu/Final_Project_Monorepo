# Experiment Report — exp_8e6d351b
**Date:** 2026-06-12T19:02:58.747379+00:00  

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
| Accuracy | 72.00% |
| 95% CI | [58.33%, 82.53%] |
| Correct / Total | 36 / 50 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1361 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 1406.7 |
| Model avg (ms) | 12228.3 |
| Summed model avg (ms) | 12228.3 |
| Model p50 (ms) | 7830.3 |
| Model p95 (ms) | 50878.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002548 |
| Total cost (USD) | $0.1274 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.1274 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.1274 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3143 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.559258 J/tok |
| Total energy (kWh) | 0.012228 |
| Avg energy per sample (kWh) | 0.00024457 |
| Total CO₂ (g) | 4.6467 |
| Avg CO₂ per sample (g) | 0.092935 |
| Normalized energy (vs baseline) | 0.2793 |

## EATS Score
**EATS = 0.5184**  
Normalized efficiency penalty: 0.6689  

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
| elementary_mathematics | 100.00% | 1 |
| formal_logic | 0.00% | 1 |
| global_facts | 0.00% | 1 |
| high_school_computer_science | 100.00% | 1 |
| high_school_geography | 33.33% | 3 |
| high_school_government_and_politics | 100.00% | 2 |
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
| professional_law | 75.00% | 8 |
| professional_medicine | 100.00% | 1 |
| professional_psychology | 0.00% | 1 |
| security_studies | 50.00% | 2 |