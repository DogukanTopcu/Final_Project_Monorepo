# Experiment Report — exp_a444a6a5
**Date:** 2026-05-26T17:30:57.282940+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | blackboard |
| Benchmark | gsm8k |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.7 |
| LLM Temperature | 0.7 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.9600 |
| llm_call_ratio | 1.0800 |
| avg_latency_ms | 8596.3678 |
| total_cost_usd | 0.4524 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.4524 |
| total_energy_kwh | 0.0616 |
| total_co2_g | 23.4081 |
| n_total | 100.0000 |
| n_correct | 96.0000 |
| eats_score | 0.8807 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 8035.5672 |
| latency_p95_ms | 13083.8747 |
| total_tokens | 32915 |
| n_escalated | 100.0000 |
| escalation_rate | 1.0000 |
| n_slm_only | 0.0000 |
| n_llm_final | 100.0000 |
| avg_slm_confidence | 0.9000 |
| avg_confidence_escalated | 0.9000 |
| avg_confidence_non_escalated | 0.0000 |
| avg_energy_per_sample_kwh | 0.0006 |
| avg_co2_per_sample_g | 0.2341 |

## EATS Score Interpretation
**EATS = 0.8807**  
Accuracy: 96.00%  
LLM Call Ratio: 108.00%  
Total Cost: $0.4524  