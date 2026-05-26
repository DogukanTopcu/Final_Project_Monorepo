# Active Oracle Architecture

This document describes the Active Oracle architecture used in the thesis system.

## Summary

Active Oracle keeps the SLM as the primary reasoner, but lets it query a truth
oracle (LLM) for narrow factual or computational sub-questions when it gets stuck.
The oracle responds concisely, and the SLM continues to produce the final answer.

Implementation: [architectures/active_oracle.py](architectures/active_oracle.py)

## Flow

1. Build a task prompt (MCQ or open-ended) and wrap it with an SLM system prompt.
2. The SLM reasons step-by-step.
3. When unsure, it emits `CALL_ORACLE: <question>`.
4. The LLM answers the sub-question concisely.
5. The SLM resumes and outputs the final answer.

## Key parameters

- `max_oracle_calls`: maximum oracle calls per sample.
- `slm_temperature`, `llm_temperature`: sampling temperatures.
- `slm_max_tokens`, `llm_max_tokens`: per-call token caps (0 = auto budget).

## Response metadata (key fields)

- `oracle_calls_made`: count of oracle calls for the sample.
- `oracle_queries`: list of questions asked to the oracle.
- `oracle_answers`: list of oracle replies.
- `slm_trace`: full SLM trace including oracle calls and answers.
- `final_answer_source`: `slm` or `none`.

## Example usage

```python
from architectures.active_oracle import ActiveOracleArchitecture
from core.models import OpenAICompatibleModel

slm = OpenAICompatibleModel(model_id="qwen3.5-4b", base_url="http://localhost:8001/v1")
llm = OpenAICompatibleModel(model_id="gpt-oss-20b", base_url="http://localhost:8002/v1")

arch = ActiveOracleArchitecture(
    slm=slm,
    llm=llm,
    max_oracle_calls=3,
    task_type="mcq",
)

response = arch.run(query)
print(response.predicted_answer)
```

## Thesis narrative summary

Active Oracle isolates narrow oracle interventions without fully escalating the
entire query to the LLM. This makes it easy to compare small, targeted LLM
assist calls against full hybrid rerouting.
