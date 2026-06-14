# Experiment Report — exp_e175bf59
**Date:** 2026-06-07T00:36:02.412326+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | multi_agent |
| Benchmark | hellaswag |
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
| Accuracy | 72.00% |
| 95% CI | [62.51%, 79.86%] |
| Correct / Total | 72 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1300 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2524.6 |
| Model avg (ms) | 21694.9 |
| Summed model avg (ms) | 21694.9 |
| Model p50 (ms) | 21550.5 |
| Model p95 (ms) | 29089.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.004520 |
| Total cost (USD) | $0.4520 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.4520 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4520 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0080 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.851884 J/tok |
| Total energy (kWh) | 0.043390 |
| Avg energy per sample (kWh) | 0.00043390 |
| Total CO₂ (g) | 16.4881 |
| Avg CO₂ per sample (g) | 0.164881 |
| Normalized energy (vs baseline) | 0.7107 |

## EATS Score
**EATS = 0.4981**  
Normalized efficiency penalty: 1.3935  
Accuracy deficit penalty: 0.1680  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | slm |
| LLM arbitration rate | 0.00% |