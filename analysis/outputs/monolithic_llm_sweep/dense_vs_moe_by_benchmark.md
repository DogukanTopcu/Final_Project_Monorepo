# Dense vs MoE by Benchmark

| benchmark | best_dense_llm | best_dense_score | best_moe | best_moe_score | score_gap_moe_minus_dense |
|---|---|---|---|---|---|
| mmlu | gemma4-31b | 0.735368 | qwen3.5-35b-a3b | 0.854064 | 0.118695 |
| arc | gpt-oss-20b | 0.745368 | qwen3.5-35b-a3b | 0.868529 | 0.123161 |
| hellaswag | gemma4-31b | 0.714954 | qwen3.5-35b-a3b | 0.966997 | 0.252043 |
| gsm8k | gemma4-31b | 0.763115 | qwen3.5-35b-a3b | 0.949737 | 0.186622 |
| truthfulqa | gemma4-31b | 0.872099 | qwen3.5-35b-a3b | 0.802849 | -0.06925 |