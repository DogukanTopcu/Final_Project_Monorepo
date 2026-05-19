# Experiment Report — exp_28f7c45d
**Date:** 2026-05-19T18:15:35.406478+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.1 |
| LLM Temperature | 0.1 |
| SLM Max Tokens | 522 |
| LLM Max Tokens | 2027 |
| SLM Only | False |
| N Samples | 20 |
| Confidence Threshold | 0.7 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.5000 |
| llm_call_ratio | 0.1000 |
| avg_latency_ms | 447.3830 |
| total_cost_usd | 0.0021 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.0021 |
| total_energy_kwh | 0.0002 |
| total_co2_g | 0.0801 |
| n_total | 20.0000 |
| n_correct | 10.0000 |
| eats_score | 4.5455 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 404.9614 |
| latency_p95_ms | 639.5478 |
| total_tokens | 3330 |
| n_escalated | 2.0000 |
| escalation_rate | 0.1000 |
| n_slm_only | 18.0000 |
| n_llm_final | 2.0000 |
| avg_slm_confidence | 0.9472 |
| avg_confidence_escalated | 0.6380 |
| avg_confidence_non_escalated | 0.9816 |
| avg_energy_per_sample_kwh | 0.0000 |
| avg_co2_per_sample_g | 0.0040 |

## EATS Score Interpretation
**EATS = 4.5455**  
Accuracy: 50.00%  
LLM Call Ratio: 10.00%  
Total Cost: $0.0021  