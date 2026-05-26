# Experiment Report — exp_f81dbd3f
**Date:** 2026-05-26T15:36:36.936293+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | arc |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.1 |
| LLM Temperature | 0.1 |
| SLM Max Tokens | 1024 |
| LLM Max Tokens | 2048 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.75 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.8900 |
| llm_call_ratio | 0.0800 |
| avg_latency_ms | 14965.9267 |
| total_cost_usd | 0.3349 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.3349 |
| total_energy_kwh | 0.0335 |
| total_co2_g | 12.7340 |
| n_total | 100.0000 |
| n_correct | 89.0000 |
| eats_score | 9.8889 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 13146.1115 |
| latency_p95_ms | 27550.0534 |
| total_tokens | 42712 |
| n_escalated | 8.0000 |
| escalation_rate | 0.0800 |
| n_slm_only | 92.0000 |
| n_llm_final | 8.0000 |
| avg_slm_confidence | 0.8607 |
| avg_confidence_escalated | 0.7084 |
| avg_confidence_non_escalated | 0.8740 |
| avg_energy_per_sample_kwh | 0.0003 |
| avg_co2_per_sample_g | 0.1273 |

## EATS Score Interpretation
**EATS = 9.8889**  
Accuracy: 89.00%  
LLM Call Ratio: 8.00%  
Total Cost: $0.3349  