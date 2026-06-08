# Experiment Report — exp_0bd43cb7
**Date:** 2026-06-08T17:40:23.300472+00:00  

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
| Escalation Rate | 55.00% |
| ECE (confidence calibration) | 0.0646 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 589.9 |
| Model avg (ms) | 8809.4 |
| Summed model avg (ms) | 8809.4 |
| Model p50 (ms) | 5626.8 |
| Model p95 (ms) | 30889.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.003177 |
| Total cost (USD) | $0.0635 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0635 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0177 |
| Escalated-path total (SLM+LLM) | $0.0459 |
| SLM-path cost fraction | 27.82% |
| Normalized cost (vs baseline) | 0.3920 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 5.322973 J/tok |
| Total energy (kWh) | 0.007684 |
| Avg energy per sample (kWh) | 0.00038422 |
| Total CO₂ (g) | 2.9200 |
| Avg CO₂ per sample (g) | 0.146002 |
| Normalized energy (vs baseline) | 0.4388 |

## EATS Score
**EATS = 0.5813**  
Normalized efficiency penalty: 0.6122  

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