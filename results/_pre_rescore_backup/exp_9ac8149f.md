# Experiment Report — exp_9ac8149f
**Date:** 2026-06-08T18:42:13.133787+00:00  

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
| Accuracy | 85.00% |
| 95% CI | [63.96%, 94.76%] |
| Correct / Total | 17 / 20 |
| Escalation Rate | 35.00% |
| ECE (confidence calibration) | 0.0724 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 562.6 |
| Model avg (ms) | 11335.1 |
| Summed model avg (ms) | 11335.1 |
| Model p50 (ms) | 7478.2 |
| Model p95 (ms) | 37334.4 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003389 |
| Total cost (USD) | $0.0678 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0678 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0274 |
| Escalated-path total (SLM+LLM) | $0.0403 |
| SLM-path cost fraction | 40.50% |
| Normalized cost (vs baseline) | 0.4181 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 4.357952 J/tok |
| Total energy (kWh) | 0.007720 |
| Avg energy per sample (kWh) | 0.00038598 |
| Total CO₂ (g) | 2.9335 |
| Avg CO₂ per sample (g) | 0.146673 |
| Normalized energy (vs baseline) | 0.4408 |

## EATS Score
**EATS = 0.5415**  
Normalized efficiency penalty: 0.7198  

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
| elementary_mathematics | 100.00% | 1 |
| high_school_geography | 0.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| machine_learning | 100.00% | 1 |
| moral_scenarios | 100.00% | 1 |
| nutrition | 100.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 75.00% | 4 |