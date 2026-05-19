from __future__ import annotations

import json

from core.types import ExperimentConfig, ExperimentResult, Query, Response, SampleResult
from evaluation.reporter import Reporter


def test_reporter_saves_routing_sample_without_escalation(tmp_path):
    result = ExperimentResult(
        experiment_id="exp_no_llm",
        config=ExperimentConfig(
            architecture="routing",
            benchmark="mmlu",
            slm_temperature=0.1,
            llm_temperature=0.2,
            slm_max_tokens=512,
            llm_max_tokens=1024,
        ),
        samples=[
            SampleResult(
                query=Query(id="q1", text="What is 2+2?", choices=["3", "4", "5", "6"], answer="B"),
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
                        "prompt_text": "Prompt body",
                        "slm_raw_text": "B",
                        "slm_parsed_answer": "B",
                        "slm_parse_status": "parsed",
                        "final_raw_text": "B",
                        "final_parsed_answer": "B",
                        "final_answer_source": "slm",
                        "escalation_reason": "accepted_by_slm_confidence",
                        "routing_decision": {
                            "accepted_by": "slm",
                            "threshold": 0.7,
                            "confidence_method": "existing_model_confidence",
                            "signals": {
                                "parse_success": True,
                                "confidence": 0.92,
                                "top2_margin": None,
                                "input_tokens": 10,
                                "input_too_long": False,
                                "low_confidence": False,
                                "low_margin": False,
                                "forced_escalation": False,
                            },
                        },
                        "final_model_id": "gemma4:latest",
                        "escalated": False,
                        "slm_confidence": 0.92,
                        "confidence_threshold": 0.7,
                        "confidence_method": "existing_model_confidence",
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
    assert sample["query_choices"] == ["3", "4", "5", "6"]
    assert sample["final_model_id"] == "gemma4:latest"
    assert sample["llm_input_tokens"] is None
    assert sample["prompt_text"] == "Prompt body"
    assert sample["slm_raw_text"] == "B"
    assert sample["slm_parsed_answer"] == "B"
    assert sample["final_raw_text"] == "B"
    assert sample["final_parsed_answer"] == "B"
    assert sample["final_answer_source"] == "slm"
    assert sample["escalation_reason"] == "accepted_by_slm_confidence"
    assert sample["routing_decision"]["accepted_by"] == "slm"
    assert sample["predicted"] == sample["final_parsed_answer"]


def test_reporter_saves_routing_sample_with_escalation(tmp_path):
    result = ExperimentResult(
        experiment_id="exp_with_llm",
        config=ExperimentConfig(
            architecture="routing",
            benchmark="mmlu",
            slm_temperature=0.05,
            llm_temperature=0.35,
            slm_max_tokens=256,
            llm_max_tokens=2048,
        ),
        samples=[
            SampleResult(
                query=Query(id="q2", text="Hard question", choices=["A1", "A2", "A3", "A4"], answer="A"),
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
                        "slm_raw_text": "SLM draft",
                        "slm_parsed_answer": "C",
                        "slm_parse_status": "parsed",
                        "llm_raw_text": "A",
                        "llm_parsed_answer": "A",
                        "llm_parse_status": "parsed",
                        "final_raw_text": "A",
                        "final_parsed_answer": "A",
                        "final_answer_source": "llm",
                        "escalation_reason": "confidence_below_threshold",
                        "routing_decision": {
                            "accepted_by": "llm",
                            "threshold": 0.7,
                            "confidence_method": "existing_model_confidence",
                            "signals": {
                                "parse_success": True,
                                "confidence": 0.41,
                                "top2_margin": None,
                                "input_tokens": 8,
                                "input_too_long": False,
                                "low_confidence": True,
                                "low_margin": False,
                                "forced_escalation": False,
                            },
                        },
                        "final_model_id": "gemini-2.5-flash",
                        "escalated": True,
                        "slm_confidence": 0.41,
                        "confidence_threshold": 0.7,
                        "confidence_method": "existing_model_confidence",
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
    assert sample["query_choices"] == ["A1", "A2", "A3", "A4"]
    assert sample["final_model_id"] == "gemini-2.5-flash"
    assert sample["llm_input_tokens"] == 14
    assert sample["llm_cost_usd"] == 0.02
    assert sample["prompt_text"] == "Prompt body"
    assert sample["slm_text"] == "SLM draft"
    assert sample["final_text"] == "A"
    assert sample["slm_raw_text"] == "SLM draft"
    assert sample["slm_parsed_answer"] == "C"
    assert sample["llm_raw_text"] == "A"
    assert sample["llm_parsed_answer"] == "A"
    assert sample["final_parsed_answer"] == "A"
    assert sample["final_answer_source"] == "llm"
    assert sample["escalation_reason"] == "confidence_below_threshold"
    assert sample["predicted"] == sample["final_parsed_answer"]


def test_reporter_includes_model_runtime_settings_in_config_and_markdown(tmp_path):
    result = ExperimentResult(
        experiment_id="exp_runtime_settings",
        config=ExperimentConfig(
            architecture="routing",
            benchmark="mmlu",
            slm_temperature=0.3,
            llm_temperature=0.6,
            slm_max_tokens=300,
            llm_max_tokens=600,
        ),
        samples=[],
    )

    path = Reporter(tmp_path).save(result)
    payload = json.loads(path.read_text())
    markdown = (tmp_path / "exp_runtime_settings.md").read_text()

    assert payload["config"]["slm_temperature"] == 0.3
    assert payload["config"]["llm_temperature"] == 0.6
    assert payload["config"]["slm_max_tokens"] == 300
    assert payload["config"]["llm_max_tokens"] == 600
    assert payload["config"]["routing_policy"]["confidence_threshold"] == 0.7
    assert payload["config"]["routing_policy"]["margin_threshold"] is None
    assert "| SLM Temperature | 0.3 |" in markdown
    assert "| LLM Max Tokens | 600 |" in markdown
