# Experiment Report — exp_ccf80089
**Date:** 2026-06-06T21:35:49.704195+00:00  

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
**EATS = 0.5124**  
Normalized efficiency penalty: 1.1766  
Accuracy deficit penalty: 0.1860  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | slm |
| LLM arbitration rate | 0.00% |