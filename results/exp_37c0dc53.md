# Experiment Report — exp_37c0dc53
**Date:** 2026-05-26T16:19:23.323574+00:00  

## Configuration
| Parameter | Value |
|-----------|-------|
| Architecture | speculative |
| Benchmark | hellaswag |
| SLM | gemma4-4b |
| LLM | gemma4-31b |
| SLM Temperature | 0.0 |
| LLM Temperature | 0.0 |
| SLM Max Tokens | 1097 |
| LLM Max Tokens | 2003 |
| SLM Only | False |
| N Samples | 100 |
| Confidence Threshold | 0.7 |

## Results
| Metric | Value |
|--------|-------|
| accuracy | 0.8100 |
| llm_call_ratio | 0.6200 |
| avg_latency_ms | 17784.6140 |
| total_cost_usd | 0.7047 |
| total_api_cost_usd | 0.0034 |
| total_infra_cost_usd | 0.7013 |
| total_energy_kwh | 0.0868 |
| total_co2_g | 32.9985 |
| n_total | 100.0000 |
| n_correct | 81.0000 |
| eats_score | 1.2857 |
| normalized_cost | 1.0000 |
| latency_p50_ms | 16489.5467 |
| latency_p95_ms | 30354.9794 |
| total_tokens | 68935 |
| n_escalated | 31.0000 |
| escalation_rate | 0.3100 |
| n_slm_only | 69.0000 |
| n_llm_final | 31.0000 |
| avg_slm_confidence | 0.8168 |
| avg_confidence_escalated | 0.7709 |
| avg_confidence_non_escalated | 0.8375 |
| avg_energy_per_sample_kwh | 0.0009 |
| avg_co2_per_sample_g | 0.3300 |

## EATS Score Interpretation
**EATS = 1.2857**  
Accuracy: 81.00%  
LLM Call Ratio: 62.00%  
Total Cost: $0.7047  