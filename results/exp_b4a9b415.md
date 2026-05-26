# Experiment Report — exp_b4a9b415
**Date:** 2026-05-26T15:08:38.412719+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | routing |
| Benchmark | gsm8k |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1024 |
| LLM Max Tokens | 2048 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.8 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.9100 |
| llm_call_ratio | 0.1900 |
| avg_latency_ms | 11511.6922 |
| total_cost_usd | 0.2888 |
| total_api_cost_usd | 0.0000 |
| total_infra_cost_usd | 0.2888 |
| total_energy_kwh | 0.0306 |
| total_co2_g | 11.6310 |
| n_total | 100.0000 |
| n_correct | 91.0000 |
| eats_score | 4.5500 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 8838.3276 |
| latency_p95_ms | 35780.4315 |
| total_tokens | 35141 |
| n_escalated | 19.0000 |
| escalation_rate | 0.1900 |
| n_slm_only | 81.0000 |
| n_llm_final | 19.0000 |
| avg_slm_confidence | 0.8758 |
| avg_confidence_escalated | 0.7721 |
| avg_confidence_non_escalated | 0.9001 |
| avg_energy_per_sample_kwh | 0.0003 |
| avg_co2_per_sample_g | 0.1163 |

## EATS Score Interpretation
**EATS = 4.5500**  
Accuracy: 91.00%  
LLM Call Ratio: 19.00%  
Total Cost: $0.2888  