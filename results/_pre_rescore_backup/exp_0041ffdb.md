# Experiment Report — exp_0041ffdb
**Date:** 2026-06-06T23:41:19.187680+00:00  

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
| Accuracy | 90.00% |
| 95% CI | [82.56%, 94.48%] |
| Correct / Total | 90 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0500 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 3057.8 |
| Model avg (ms) | 13214.9 |
| Summed model avg (ms) | 13214.9 |
| Model p50 (ms) | 13220.0 |
| Model p95 (ms) | 16669.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005803 |
| Total cost (USD) | $0.5803 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5803 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.5803 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.2942 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.565877 J/tok |
| Total energy (kWh) | 0.073700 |
| Avg energy per sample (kWh) | 0.00073700 |
| Total CO₂ (g) | 28.0061 |
| Avg CO₂ per sample (g) | 0.280061 |
| Normalized energy (vs baseline) | 1.2071 |

## EATS Score
**EATS = 0.3804**  
Normalized efficiency penalty: 1.4657  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | llm |
| LLM arbitration rate | 100.00% |