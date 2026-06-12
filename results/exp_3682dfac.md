# Experiment Report — exp_3682dfac
**Date:** 2026-06-10T22:25:56.053874+00:00  

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
| N Samples | 10 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 90.00% |
| 95% CI | [59.58%, 98.21%] |
| Correct / Total | 9 / 10 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1164 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 281.7 |
| Model avg (ms) | 8132.7 |
| Summed model avg (ms) | 8132.7 |
| Model p50 (ms) | 6621.3 |
| Model p95 (ms) | 17819.1 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.001694 |
| Total cost (USD) | $0.0169 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.0169 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0169 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.2090 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.555891 J/tok |
| Total energy (kWh) | 0.001627 |
| Avg energy per sample (kWh) | 0.00016265 |
| Total CO₂ (g) | 0.6181 |
| Avg CO₂ per sample (g) | 0.061809 |
| Normalized energy (vs baseline) | 0.1858 |

## EATS Score
**EATS = 0.6692**  
Normalized efficiency penalty: 0.4449  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Accuracy by Subject
| Subject | Accuracy | N |
|---|---|---|
| business_ethics | 100.00% | 1 |
| conceptual_physics | 100.00% | 1 |
| econometrics | 100.00% | 1 |
| elementary_mathematics | 100.00% | 1 |
| high_school_government_and_politics | 100.00% | 1 |
| high_school_macroeconomics | 100.00% | 1 |
| high_school_microeconomics | 100.00% | 1 |
| professional_accounting | 100.00% | 1 |
| professional_law | 50.00% | 2 |