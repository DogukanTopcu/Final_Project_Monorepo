# Experiment Report — exp_cb8c7193
**Date:** 2026-06-08T18:34:36.613945+00:00  

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
| N Samples | 20 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 80.00% |
| 95% CI | [58.40%, 91.93%] |
| Correct / Total | 16 / 20 |
| Escalation Rate | 35.00% |
| ECE (confidence calibration) | 0.1112 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 555.9 |
| Model avg (ms) | 10783.6 |
| Summed model avg (ms) | 10783.6 |
| Model p50 (ms) | 7465.8 |
| Model p95 (ms) | 37323.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003271 |
| Total cost (USD) | $0.0654 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0654 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0252 |
| Escalated-path total (SLM+LLM) | $0.0402 |
| SLM-path cost fraction | 38.59% |
| Normalized cost (vs baseline) | 0.4035 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.497103 J/tok |
| Total energy (kWh) | 0.007489 |
| Avg energy per sample (kWh) | 0.00037445 |
| Total CO₂ (g) | 2.8458 |
| Avg CO₂ per sample (g) | 0.142290 |
| Normalized energy (vs baseline) | 0.4276 |

## EATS Score
**EATS = 0.5372**  
Normalized efficiency penalty: 0.6893  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| business_ethics | 100.00% | 1 |
| clinical_knowledge | 50.00% | 2 |
| college_physics | 100.00% | 1 |
| computer_security | 100.00% | 1 |
| conceptual_physics | 100.00% | 1 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 0.00% | 1 |
| high_school_geography | 0.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| machine_learning | 100.00% | 1 |
| moral_scenarios | 100.00% | 1 |
| nutrition | 100.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 75.00% | 4 |