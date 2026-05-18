from __future__ import annotations

import json

from core.types import ExperimentConfig, ExperimentResult, Query, Response, SampleResult
from evaluation.reporter import Reporter


def test_reporter_saves_routing_sample_without_escalation(tmp_path):
    result = ExperimentResult(
        experiment_id="exp_no_llm",
        config=ExperimentConfig(architecture="routing", benchmark="mmlu"),
        samples=[
            SampleResult(
                query=Query(id="q1", text="What is 2+2?", answer="B"),
                response=Response(
                    query_id="q1",
                    text="B",
                    predicted_answer="B",
                    confidence=0.92,
                    model_id="gemma4:latest",
                    latency_ms=25.0,
                    input_tokens=10,
                    output_tokens=3,
                    cost_usd=0.0,
                    llm_calls=0,
                    metadata={
                        "final_model_id": "gemma4:latest",
                        "escalated": False,
                        "slm_confidence": 0.92,
                        "confidence_threshold": 0.7,
                        "slm_latency_ms": 25.0,
                        "slm_input_tokens": 10,
                        "slm_output_tokens": 3,
                        "slm_cost_usd": 0.0,
                    },
                ),
                correct=True,
            )
        ],
    )

    path = Reporter(tmp_path).save(result)
    payload = json.loads(path.read_text())
    sample = payload["samples"][0]

    assert sample["escalated"] is False
    assert sample["final_model_id"] == "gemma4:latest"
    assert sample["llm_input_tokens"] is None
    assert "prompt_text" not in sample


def test_reporter_saves_routing_sample_with_escalation(tmp_path):
    result = ExperimentResult(
        experiment_id="exp_with_llm",
        config=ExperimentConfig(architecture="routing", benchmark="mmlu"),
        samples=[
            SampleResult(
                query=Query(id="q2", text="Hard question", answer="A"),
                response=Response(
                    query_id="q2",
                    text="A",
                    predicted_answer="A",
                    confidence=0.41,
                    model_id="gemini-2.5-flash",
                    latency_ms=80.0,
                    input_tokens=22,
                    output_tokens=8,
                    cost_usd=0.02,
                    llm_calls=1,
                    metadata={
                        "prompt_text": "Prompt body",
                        "slm_text": "SLM draft",
                        "final_model_id": "gemini-2.5-flash",
                        "escalated": True,
                        "slm_confidence": 0.41,
                        "confidence_threshold": 0.7,
                        "slm_latency_ms": 20.0,
                        "slm_input_tokens": 8,
                        "slm_output_tokens": 4,
                        "slm_cost_usd": 0.0,
                        "llm_latency_ms": 60.0,
                        "llm_input_tokens": 14,
                        "llm_output_tokens": 4,
                        "llm_cost_usd": 0.02,
                    },
                ),
                correct=True,
            )
        ],
    )

    path = Reporter(tmp_path).save(result)
    payload = json.loads(path.read_text())
    sample = payload["samples"][0]

    assert sample["escalated"] is True
    assert sample["final_model_id"] == "gemini-2.5-flash"
    assert sample["llm_input_tokens"] == 14
    assert sample["llm_cost_usd"] == 0.02
    assert sample["prompt_text"] == "Prompt body"
    assert sample["slm_text"] == "SLM draft"
    assert sample["final_text"] == "A"
