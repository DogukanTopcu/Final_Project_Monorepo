# Experiment Report — exp_ecdd81b2
**Date:** 2026-05-26T14:01:10.854256+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | mmlu |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 567 |
| LLM Max Tokens | 1082 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.8 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.7600 |
| llm_call_ratio | 0.3400 |
| avg_latency_ms | 20446.6140 |
| total_cost_usd | 0.5913 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.5913 |
| total_energy_kwh | 0.0665 |
| total_co2_g | 25.2750 |
| n_total | 100.0000 |
| n_correct | 76.0000 |
| eats_score | 2.1714 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 19365.6183 |
| latency_p95_ms | 42184.8480 |
| total_tokens | 69512 |
| n_escalated | 34.0000 |
| escalation_rate | 0.3400 |
| n_slm_only | 66.0000 |
| n_llm_final | 34.0000 |
| avg_slm_confidence | 0.8525 |
| avg_confidence_escalated | 0.7793 |
| avg_confidence_non_escalated | 0.8902 |
| avg_energy_per_sample_kwh | 0.0007 |
| avg_co2_per_sample_g | 0.2528 |

## EATS Score Interpretation
**EATS = 2.1714**  
Accuracy: 76.00%  
LLM Call Ratio: 34.00%  
Total Cost: $0.5913  