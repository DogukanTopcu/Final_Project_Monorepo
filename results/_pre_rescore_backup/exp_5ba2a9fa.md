# Experiment Report — exp_5ba2a9fa
**Date:** 2026-06-13T00:26:27.907508+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | pure_swarm |
| Benchmark | hellaswag |
| SLM | gemma4-4b |
| LLM | None |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 2000 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 65.00% |
| 95% CI | [55.25%, 73.64%] |
| Correct / Total | 65 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.0891 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2586.4 |
| Model avg (ms) | 10067.2 |
| Summed model avg (ms) | 10067.2 |
| Model p50 (ms) | 8014.7 |
| Model p95 (ms) | 29023.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.002097 |
| Total cost (USD) | $0.2097 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.2097 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.2097 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.3099 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.783775 J/tok |
| Total energy (kWh) | 0.020134 |
| Avg energy per sample (kWh) | 0.00020134 |
| Total CO₂ (g) | 7.6511 |
| Avg CO₂ per sample (g) | 0.076511 |
| Normalized energy (vs baseline) | 0.2779 |

## EATS Score
**EATS = 0.4976**  
Normalized efficiency penalty: 0.6562  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.