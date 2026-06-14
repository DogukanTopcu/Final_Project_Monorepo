# Experiment Report — exp_abf962fe
**Date:** 2026-06-07T03:06:01.563586+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | multi_agent |
| Benchmark | truthfulqa |
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
| Accuracy | 87.00% |
| 95% CI | [79.02%, 92.24%] |
| Correct / Total | 87 / 100 |
| Escalation Rate | 100.00% |
| ECE (confidence calibration) | 0.0200 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 3014.9 |
| Model avg (ms) | 12022.0 |
| Summed model avg (ms) | 12022.0 |
| Model p50 (ms) | 12086.1 |
| Model p95 (ms) | 19388.7 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005037 |
| Total cost (USD) | $0.5037 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5037 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.0000 |
| Escalated-path total (SLM+LLM) | $0.5037 |
| SLM-path cost fraction | 0.00% |
| Normalized cost (vs baseline) | 1.4395 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 6.286822 J/tok |
| Total energy (kWh) | 0.063296 |
| Avg energy per sample (kWh) | 0.00063296 |
| Total CO₂ (g) | 24.0525 |
| Avg CO₂ per sample (g) | 0.240525 |
| Normalized energy (vs baseline) | 1.3284 |

## EATS Score
**EATS = 0.5502**  
Normalized efficiency penalty: 1.5835  
Accuracy deficit penalty: 0.0780  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | llm |
| LLM arbitration rate | 100.00% |