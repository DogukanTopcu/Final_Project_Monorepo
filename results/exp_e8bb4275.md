# Experiment Report — exp_e8bb4275
**Date:** 2026-06-03T21:13:53.648640+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | ensemble |
| Benchmark | mmlu |
| SLM | None |
| LLM | None |
| SLM Temperature | 0.4 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1420 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Accuracy
| Metric | Value |
|--------|-------|
| Accuracy | 59.00% |
| 95% CI | [49.20%, 68.13%] |
| Correct / Total | 59 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.2465 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2157.1 |
| Model avg (ms) | 26935.5 |
| Summed model avg (ms) | 26935.5 |
| Model p50 (ms) | 24110.4 |
| Model p95 (ms) | 66524.0 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005612 |
| Total cost (USD) | $0.5612 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5612 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.5612 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 1.0000 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 3.337843 J/tok |
| Total energy (kWh) | 0.053871 |
| Avg energy per sample (kWh) | 0.00053871 |
| Total CO₂ (g) | 20.4710 |
| Avg CO₂ per sample (g) | 0.204710 |
| Normalized energy (vs baseline) | 1.0000 |

## EATS Score
**EATS = 0.4773**  
Normalized efficiency penalty: 1.0000  
Accuracy deficit penalty: 0.2460  

> EATS = accuracy / (accuracy + 0.40 × efficiency penalty + 0.60 × (1 - accuracy)).  
> Efficiency penalty = 0.65 × normalized cost + 0.20 × normalized latency + 0.15 × normalized energy.

## Ensemble Breakdown
| Path | Accuracy | N queries |
|------|----------|-----------|
| Majority vote (no tiebreak) | 59.00% | 100 |
| LLM tiebreak | 0.00% | 0 |
| Tiebreak rate | 0.00% | — |