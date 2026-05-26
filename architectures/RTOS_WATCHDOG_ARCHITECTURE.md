# RTOS Watchdog Architecture

This document describes the RTOS Watchdog architecture used in the thesis system.

## Summary

RTOS Watchdog streams SLM tokens with logprob telemetry. A watchdog checks token
confidence in real time and interrupts to a heavier LLM when confidence drops
below a threshold. The LLM completes the answer from the partial prefix.

Implementation: [architectures/rtos_watchdog.py](architectures/rtos_watchdog.py)

## Flow

1. Build a task prompt (MCQ or open-ended).
2. Start an OpenAI-compatible streaming request to the SLM with logprobs enabled.
3. For each token, compute probability from logprob.
4. If probability < `confidence_threshold`, interrupt the stream.
5. Hand off to the LLM with the partial prefix for completion.

## Key parameters

- `confidence_threshold`: interrupt threshold for token probability.
- `slm_temperature`, `llm_temperature`: sampling temperatures.
- `slm_max_tokens`, `llm_max_tokens`: per-call token caps.

## Response metadata (key fields)

- `interrupted`: whether the watchdog triggered a handoff.
- `slm_prefix`: partial text produced before the interrupt.
- `slm_tokens_before_interrupt`: number of streamed tokens before interruption.
- `final_answer_source`: `slm` or `llm`.

## Example usage

```python
from architectures.rtos_watchdog import RTOSWatchdogArchitecture
from core.models import OpenAICompatibleModel

slm = OpenAICompatibleModel(model_id="qwen3.5-4b", base_url="http://localhost:8001/v1")
llm = OpenAICompatibleModel(model_id="gpt-oss-20b", base_url="http://localhost:8002/v1")

arch = RTOSWatchdogArchitecture(
    slm=slm,
    llm=llm,
    confidence_threshold=0.6,
    task_type="mcq",
)

response = arch.run(query)
print(response.predicted_answer)
```

## Notes

- The SLM streaming path expects an OpenAI-compatible `/chat/completions` endpoint.
- If streaming fails, the architecture falls back to the LLM by design.

## Thesis narrative summary

RTOS Watchdog simulates real-time interrupt handling: small models run fast until
uncertainty rises, then a heavier model takes over. It makes the tradeoff between
low-latency local decoding and safe LLM completion explicit.
