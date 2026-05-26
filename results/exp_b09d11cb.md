# Experiment Report — exp_b09d11cb
**Date:** 2026-05-26T18:13:57.945651+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | active_oracle |
| Benchmark | gsm8k |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 0 |
| LLM Max Tokens | 0 |
| SLM Only | False |
| N Samples | 200 |
| Confidence Threshold | 0.7 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.9250 |
| llm_call_ratio | 0.0300 |
| avg_latency_ms | 18711.0839 |
| total_cost_usd | 0.7853 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.7853 |
| total_energy_kwh | 0.0757 |
| total_co2_g | 28.7767 |
| n_total | 200.0000 |
| n_correct | 185.0000 |
| eats_score | 23.1250 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 17471.9529 |
| latency_p95_ms | 31516.2955 |
| total_tokens | 234432 |
| n_escalated | 6.0000 |
| escalation_rate | 0.0300 |
| n_slm_only | 194.0000 |
| n_llm_final | 6.0000 |
| avg_slm_confidence | 0.9942 |
| avg_confidence_escalated | 0.9796 |
| avg_confidence_non_escalated | 0.9946 |
| avg_energy_per_sample_kwh | 0.0004 |
| avg_co2_per_sample_g | 0.1439 |

## EATS Score Interpretation
**EATS = 23.1250**  
Accuracy: 92.50%  
LLM Call Ratio: 3.00%  
Total Cost: $0.7853  