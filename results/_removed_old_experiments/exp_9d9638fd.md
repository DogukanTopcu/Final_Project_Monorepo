# Experiment Report — exp_9d9638fd
**Date:** 2026-06-02T23:05:51.481823+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
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
| Accuracy | 74.00% |
| 95% CI | [64.63%, 81.60%] |
| Correct / Total | 74 / 100 |
| Escalation Rate | 15.00% |
| ECE (confidence calibration) | 0.1630 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2218.1 |
| Model avg (ms) | 30636.2 |
| Summed model avg (ms) | 30636.2 |
| Model p50 (ms) | 25293.1 |
| Model p95 (ms) | 64346.6 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.006594 |
| Total cost (USD) | $0.6594 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.6594 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.4486 |
| Escalated-path total (SLM+LLM) | $0.2108 |
| SLM-path cost fraction | 68.03% |
| Normalized cost (vs baseline) | 1.0539 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.419709 J/tok |
| Total energy (kWh) | 0.064550 |
| Avg energy per sample (kWh) | 0.00064550 |
| Total CO₂ (g) | 24.5289 |
| Avg CO₂ per sample (g) | 0.245289 |
| Normalized energy (vs baseline) | 0.7577 |

## EATS Score
**EATS = 0.5030**  
Normalized efficiency penalty: 1.4380  
Accuracy deficit penalty: 0.1560  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Active Oracle Breakdown
| Metric | Value |
|--------|-------|
| Oracle query rate | 15.00% |
| LLM calls total | 15 |