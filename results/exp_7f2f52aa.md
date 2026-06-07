# Experiment Report — exp_7f2f52aa
**Date:** 2026-06-07T02:29:01.614633+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | multi_agent |
| Benchmark | gsm8k |
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
| Accuracy | 95.00% |
| 95% CI | [88.82%, 97.85%] |
| Correct / Total | 95 / 100 |
| Escalation Rate | 0.00% |
| ECE (confidence calibration) | 0.1000 |

## Latency
| Metric | Value |
|--------|-------|
| Throughput (output tok/s) | 2526.1 |
| Model avg (ms) | 24670.0 |
| Summed model avg (ms) | 24670.0 |
| Model p50 (ms) | 23245.7 |
| Model p95 (ms) | 40746.3 |

> Latency metrics use model-reported inference time when available and fall back to observed timing otherwise.

## Cost
| Metric | Value |
|--------|-------|
| Cost per query (USD) | $0.005140 |
| Total cost (USD) | $0.5140 |
| API cost (USD) | $0.0000 |
| Infra cost (USD) | $0.5140 |
| SLM API cost — all queries (USD) | $0.0000 |
| LLM API cost — escalated only (USD) | $0.0000 |
| SLM-path total (non-escalated queries) | $0.5140 |
| Escalated-path total (SLM+LLM) | $0.0000 |
| SLM-path cost fraction | 100.00% |
| Normalized cost (vs baseline) | 0.8835 |

## Energy
| Metric | Value |
|--------|-------|
| **Joules per output token** | 2.850285 J/tok |
| Total energy (kWh) | 0.049340 |
| Avg energy per sample (kWh) | 0.00049340 |
| Total CO₂ (g) | 18.7492 |
| Avg CO₂ per sample (g) | 0.187492 |
| Normalized energy (vs baseline) | 0.6229 |

## EATS Score
**EATS = 0.4048**  
Normalized efficiency penalty: 1.3969  

> EATS = accuracy / (accuracy + efficiency penalty).  
> Efficiency penalty = 0.5 × normalized cost + 0.3 × normalized latency + 0.2 × normalized energy.

## Multi-Agent Breakdown
| Metric | Value |
|--------|-------|
| Arbitrator | slm |
| LLM arbitration rate | 0.00% |