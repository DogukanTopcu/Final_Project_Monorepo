"""Unit tests for architectures — uses a stub ModelProvider (no API calls)."""
from __future__ import annotations

import time
from unittest.mock import MagicMock

from architectures.active_oracle import ActiveOracleArchitecture
from architectures.ensemble import EnsembleArchitecture
from architectures.multi_agent import MultiAgentArchitecture
from architectures.routing import RoutingArchitecture, should_escalate
from architectures.speculative_decoding import SpeculativeDecodingArchitecture
from core.models import ModelProvider
from core.types import Query


class StubModel(ModelProvider):
    """Returns a fixed answer with configurable confidence."""

    def __init__(
        self,
        model_id: str,
        answer: str = "A",
        confidence: float | None = 0.9,
    ) -> None:
        super().__init__(model_id)
        self._answer = answer
        self._confidence = confidence

    def generate(self, prompt: str, **kwargs):
        return self._answer, self._confidence, 10, 5, 0.0


class RecordingStubModel(StubModel):
    def __init__(self, model_id: str, answer: str = "A", confidence: float = 0.9) -> None:
        super().__init__(model_id, answer=answer, confidence=confidence)
        self.calls: list[dict] = []

    def generate(self, prompt: str, **kwargs):
        self.calls.append(kwargs)
        return super().generate(prompt, **kwargs)


class SequenceRecordingStubModel(RecordingStubModel):
    def __init__(self, model_id: str, answers: list[str], confidence: float = 0.9) -> None:
        super().__init__(model_id, answer=answers[0], confidence=confidence)
        self._answers = iter(answers)

    def generate(self, prompt: str, **kwargs):
        self.calls.append(kwargs)
        return next(self._answers), self._confidence, 10, 5, 0.0


class MetadataStubModel(RecordingStubModel):
    def __init__(
        self,
        model_id: str,
        answer: str = "A",
        confidence: float = 0.9,
        *,
        finish_reason: str = "stop",
        effective_max_tokens: int = 0,
    ) -> None:
        super().__init__(model_id, answer=answer, confidence=confidence)
        self._finish_reason = finish_reason
        self._effective_max_tokens = effective_max_tokens

    def generate(self, prompt: str, **kwargs):
        self.calls.append(kwargs)
        self.last_generation_metadata = {
            "finish_reason": self._finish_reason,
            "effective_max_tokens": self._effective_max_tokens,
        }
        return super().generate(prompt, **kwargs)


class SlowStubModel(StubModel):
    def __init__(
        self,
        model_id: str,
        answer: str = "A",
        confidence: float | None = 0.9,
        *,
        delay_s: float = 0.15,
    ) -> None:
        super().__init__(model_id, answer=answer, confidence=confidence)
        self.delay_s = delay_s

    def generate(self, prompt: str, **kwargs):
        time.sleep(self.delay_s)
        return super().generate(prompt, **kwargs)


QUERY = Query(
    id="q1",
    text="What is 2+2?",
    choices=["3", "4", "5", "6"],
    answer="B",
)


class TestRoutingArchitecture:
    def test_should_escalate_parse_failure(self):
        escalate, reason, signals = should_escalate(
            parsed_answer=None,
            confidence=0.95,
            confidence_threshold=0.7,
        )
        assert escalate is True
        assert reason == "parse_failed"
        assert signals["parse_success"] is False

    def test_should_escalate_low_confidence(self):
        escalate, reason, _ = should_escalate(
            parsed_answer="A",
            confidence=0.4,
            confidence_threshold=0.7,
        )
        assert escalate is True
        assert reason == "confidence_below_threshold"

    def test_should_accept_high_confidence(self):
        escalate, reason, _ = should_escalate(
            parsed_answer="A",
            confidence=0.9,
            confidence_threshold=0.7,
        )
        assert escalate is False
        assert reason == "accepted_by_slm_confidence"

    def test_should_escalate_missing_confidence(self):
        escalate, reason, _ = should_escalate(
            parsed_answer="A",
            confidence=None,
            confidence_threshold=0.7,
        )
        assert escalate is True
        assert reason == "missing_confidence"

    def test_should_escalate_long_input_when_threshold_is_set(self):
        escalate, reason, signals = should_escalate(
            parsed_answer="A",
            confidence=0.9,
            confidence_threshold=0.7,
            input_tokens=500,
            long_input_token_threshold=250,
        )
        assert escalate is True
        assert reason == "input_too_long"
        assert signals["input_too_long"] is True

    def test_should_escalate_low_margin_when_available(self):
        escalate, reason, signals = should_escalate(
            parsed_answer="A",
            confidence=0.9,
            confidence_threshold=0.7,
            top2_margin=0.05,
            margin_threshold=0.1,
        )
        assert escalate is True
        assert reason == "top2_margin_below_threshold"
        assert signals["low_margin"] is True

    def test_unavailable_margin_does_not_escalate_by_itself(self):
        escalate, reason, signals = should_escalate(
            parsed_answer="A",
            confidence=0.9,
            confidence_threshold=0.7,
            top2_margin=None,
            margin_threshold=0.1,
        )
        assert escalate is False
        assert reason == "accepted_by_slm_confidence"
        assert signals["top2_margin"] is None

    def test_high_confidence_uses_slm_only(self):
        slm = StubModel("slm", answer="B", confidence=0.9)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)
        assert resp.llm_calls == 0
        assert resp.model_id == "slm"

    def test_low_confidence_escalates_to_llm(self):
        slm = StubModel("slm", answer="A", confidence=0.3)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)
        assert resp.llm_calls == 1
        assert resp.model_id == "llm"

    def test_response_has_predicted_answer(self):
        slm = StubModel("slm", answer="B", confidence=0.9)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm)
        resp = arch.run(QUERY)
        assert resp.predicted_answer == "B"

    def test_non_escalated_response_contains_observability_fields(self):
        slm = StubModel("slm", answer="B", confidence=0.9)
        llm = StubModel("llm", answer="A", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)

        assert resp.metadata["slm_raw_text"] == "B"
        assert resp.metadata["slm_parsed_answer"] == "B"
        assert resp.metadata["final_raw_text"] == "B"
        assert resp.metadata["final_parsed_answer"] == "B"
        assert resp.metadata["final_answer_source"] == "slm"
        assert resp.metadata["escalation_reason"] == "accepted_by_slm_confidence"
        assert resp.metadata["routing_decision"]["accepted_by"] == "slm"
        assert resp.predicted_answer == resp.metadata["final_parsed_answer"]

    def test_unparseable_slm_answer_escalates_even_with_high_confidence(self):
        slm = StubModel("slm", answer="I am not sure", confidence=0.91)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)
        assert resp.llm_calls == 1
        assert resp.model_id == "llm"

    def test_escalated_response_contains_slm_and_llm_observability_fields(self):
        slm = StubModel("slm", answer="A", confidence=0.3)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)

        assert resp.metadata["slm_raw_text"] == "A"
        assert resp.metadata["slm_parsed_answer"] == "A"
        assert resp.metadata["llm_raw_text"] == "B"
        assert resp.metadata["llm_parsed_answer"] == "B"
        assert resp.metadata["final_raw_text"] == "B"
        assert resp.metadata["final_parsed_answer"] == "B"
        assert resp.metadata["final_answer_source"] == "llm"
        assert resp.metadata["escalation_reason"] == "confidence_below_threshold"
        assert resp.metadata["routing_decision"]["accepted_by"] == "llm"
        assert resp.predicted_answer == resp.metadata["final_parsed_answer"]

    def test_llm_parse_failure_returns_null_final_answer(self):
        slm = StubModel("slm", answer="A", confidence=0.2)
        llm = StubModel("llm", answer="not a letter", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 1
        assert resp.predicted_answer is None
        assert resp.metadata["llm_parse_status"] == "unparseable"
        assert resp.metadata["final_parsed_answer"] is None
        assert resp.metadata["final_answer_source"] == "none"

    def test_routing_passes_per_model_generation_settings(self):
        slm = RecordingStubModel("slm", answer="A", confidence=0.2)
        llm = RecordingStubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(
            slm=slm,
            llm=llm,
            confidence_threshold=0.7,
            slm_temperature=0.15,
            llm_temperature=0.65,
            slm_max_tokens=128,
            llm_max_tokens=256,
        )
        arch.run(QUERY)

        assert slm.calls[0] == {"temperature": 0.15, "max_tokens": 128}
        assert llm.calls[0] == {"temperature": 0.65, "max_tokens": 256}

    def test_routing_mcq_prompt_is_compact_and_latency_uses_model_time(self, monkeypatch):
        slm = RecordingStubModel("slm", answer="B", confidence=0.9)
        llm = RecordingStubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, task_type="mcq")

        captured_prompts: list[str] = []

        def fake_timed_generate(provider, prompt, **kwargs):
            captured_prompts.append(prompt)
            provider.last_generation_metadata = {"wall_latency_ms": 120.0}
            return "Answer: B", 0.9, 10, 5, 0.0, 25.0

        monkeypatch.setattr(arch, "_timed_generate", fake_timed_generate)
        resp = arch.run(QUERY)

        assert "Keep the rationale extremely short." in captured_prompts[0]
        assert resp.latency_ms == 25.0
        assert resp.algorithmic_latency_ms == 25.0
        assert resp.metadata["wall_latency_ms"] == 120.0

    def test_routing_slm_only_never_calls_llm(self):
        slm = RecordingStubModel("slm", answer="B", confidence=0.1)
        llm = RecordingStubModel("llm", answer="A", confidence=0.9)
        arch = RoutingArchitecture(
            slm=slm,
            llm=llm,
            confidence_threshold=0.95,
            slm_only=True,
        )
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id == "slm"
        assert llm.calls == []


class TestSpeculativeDecodingArchitecture:
    def test_verified_draft_is_returned_when_verifier_matches(self, monkeypatch):
        calls: list[dict] = []

        class FakeResponse:
            def __init__(self, payload: dict, status_code: int = 200) -> None:
                self._payload = payload
                self.status_code = status_code
                self.headers = {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"{self.status_code} Client Error")
                return None

            def json(self):
                return self._payload

        def fake_post(url: str, json: dict, headers: dict, timeout: float):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
            model = json["model"]
            if model == "Qwen/Qwen3.5-4B":
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Answer: B"},
                                "logprobs": {
                                    "content": [
                                        {"token": "Answer", "logprob": -0.01},
                                        {"token": ": ", "logprob": -0.01},
                                        {"token": "B", "logprob": -0.01},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                    }
                )
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {"content": "Answer: B"},
                            "logprobs": {
                                "content": [
                                    {"token": "Answer", "logprob": -0.02},
                                    {"token": ": ", "logprob": -0.02},
                                    {"token": "B", "logprob": -0.02},
                                ]
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 18, "completion_tokens": 3},
                }
            )

        monkeypatch.setattr("architectures.speculative_decoding.requests.post", fake_post)

        arch = SpeculativeDecodingArchitecture(
            drafter_url="http://draft/v1",
            verifier_url="http://verify/v1",
            task_type="mcq",
            verifier_lookahead_tokens=4,
        )
        resp = arch.run(QUERY)

        assert resp.text == "Answer: B"
        assert resp.predicted_answer == "B"
        assert resp.model_id == "Qwen/Qwen3.5-4B"
        assert resp.llm_calls == 1
        assert resp.metadata["rewrite_triggered"] is False
        assert resp.metadata["final_answer_source"] == "verified_draft"
        assert resp.metadata["accepted_draft_chars"] == len("Answer: B")
        assert resp.metadata["verifier_requests"] == 1
        assert len(resp.metadata["verification_steps"]) == 1
        assert resp.metadata["llm_raw_text"] is None
        assert calls[1]["json"]["messages"] == [calls[1]["json"]["messages"][0]]

    def test_verifier_rewrites_suffix_from_accepted_prefix(self, monkeypatch):
        calls: list[dict] = []

        class FakeResponse:
            def __init__(self, payload: dict, status_code: int = 200) -> None:
                self._payload = payload
                self.status_code = status_code
                self.headers = {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"{self.status_code} Client Error")
                return None

            def json(self):
                return self._payload

        def fake_post(url: str, json: dict, headers: dict, timeout: float):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
            model = json["model"]
            if model == "Qwen/Qwen3.5-4B":
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Answer: B"},
                                "logprobs": {
                                    "content": [
                                        {"token": "Answer", "logprob": -0.01},
                                        {"token": ": ", "logprob": -0.01},
                                        {"token": "B", "logprob": -0.01},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                    }
                )

            if len(calls) == 2:
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Answer: C"},
                                "logprobs": {
                                    "content": [
                                        {"token": "Answer", "logprob": -0.02},
                                        {"token": ": ", "logprob": -0.02},
                                        {"token": "C", "logprob": -0.02},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 18, "completion_tokens": 3},
                    }
                )

            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {"content": "C"},
                            "logprobs": {"content": [{"token": "C", "logprob": -0.02}]},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 1},
                }
            )

        monkeypatch.setattr("architectures.speculative_decoding.requests.post", fake_post)

        arch = SpeculativeDecodingArchitecture(
            drafter_url="http://draft/v1",
            verifier_url="http://verify/v1",
            task_type="mcq",
            verifier_lookahead_tokens=4,
        )
        resp = arch.run(QUERY)

        assert resp.text == "Answer: C"
        assert resp.predicted_answer == "C"
        assert resp.model_id == "meta-llama/Llama-3.3-70B-Instruct"
        assert resp.metadata["rewrite_triggered"] is True
        assert resp.metadata["rewrite_reason"] == "verifier_diverged_from_draft"
        assert resp.metadata["accepted_prefix_text"] == "Answer: "
        assert resp.metadata["final_answer_source"] == "verifier_rewrite"
        rewrite_payload = calls[2]["json"]
        assert rewrite_payload["continue_final_message"] is True
        assert rewrite_payload["messages"][-1] == {"role": "assistant", "content": "Answer: "}

    def test_continuation_falls_back_when_endpoint_rejects_prefill(self, monkeypatch):
        calls: list[dict] = []

        class FakeResponse:
            def __init__(self, payload: dict, status_code: int = 200) -> None:
                self._payload = payload
                self.status_code = status_code
                self.headers = {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"{self.status_code} Client Error")
                return None

            def json(self):
                return self._payload

        def fake_post(url: str, json: dict, headers: dict, timeout: float):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
            model = json["model"]
            if model == "Qwen/Qwen3.5-4B":
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Answer: B"},
                                "logprobs": {
                                    "content": [
                                        {"token": "Answer", "logprob": -0.01},
                                        {"token": ": ", "logprob": -0.01},
                                        {"token": "B", "logprob": -0.01},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                    }
                )
            if json.get("continue_final_message") is True:
                return FakeResponse({"error": {"message": "unsupported"}}, status_code=400)
            if len(calls) == 2:
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Answer: "},
                                "logprobs": {
                                    "content": [
                                        {"token": "Answer", "logprob": -0.02},
                                        {"token": ": ", "logprob": -0.02},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 20, "completion_tokens": 2},
                    }
                )
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {"content": "B"},
                            "logprobs": {"content": [{"token": "B", "logprob": -0.02}]},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 20, "completion_tokens": 1},
                }
            )

        monkeypatch.setattr("architectures.speculative_decoding.requests.post", fake_post)

        arch = SpeculativeDecodingArchitecture(
            drafter_url="http://draft/v1",
            verifier_url="http://verify/v1",
            task_type="mcq",
            verifier_lookahead_tokens=2,
        )
        resp = arch.run(QUERY)

        assert resp.predicted_answer == "B"
        assert resp.metadata["continuation_fallback_used"] is True
        assert calls[2]["json"]["continue_final_message"] is True
        assert "continue_final_message" not in calls[3]["json"]
        assert "Accepted prefix:" in calls[3]["json"]["messages"][0]["content"]

    def test_tolerant_mcq_verification_accepts_same_answer_with_different_wording(self, monkeypatch):
        calls: list[dict] = []

        class FakeResponse:
            def __init__(self, payload: dict, status_code: int = 200) -> None:
                self._payload = payload
                self.status_code = status_code
                self.headers = {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise RuntimeError(f"{self.status_code} Client Error")
                return None

            def json(self):
                return self._payload

        def fake_post(url: str, json: dict, headers: dict, timeout: float):
            calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
            if json["model"] == "Qwen/Qwen3.5-4B":
                return FakeResponse(
                    {
                        "choices": [
                            {
                                "message": {"content": "Here's the short reason. Answer: B"},
                                "logprobs": {
                                    "content": [
                                        {"token": "Here", "logprob": -0.01},
                                        {"token": "B", "logprob": -0.01},
                                    ]
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 12, "completion_tokens": 7},
                    }
                )
            return FakeResponse(
                {
                    "choices": [
                        {
                            "message": {"content": "The correct option is B.\nAnswer: B"},
                            "logprobs": {
                                "content": [
                                    {"token": "Answer", "logprob": -0.02},
                                    {"token": "B", "logprob": -0.02},
                                ]
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 18, "completion_tokens": 8},
                }
            )

        monkeypatch.setattr("architectures.speculative_decoding.requests.post", fake_post)

        arch = SpeculativeDecodingArchitecture(
            drafter_url="http://draft/v1",
            verifier_url="http://verify/v1",
            task_type="mcq",
            verifier_lookahead_tokens=12,
            draft_max_tokens=32,
        )
        resp = arch.run(QUERY)

        assert "Keep the rationale extremely short." in calls[0]["json"]["messages"][0]["content"]
        assert calls[0]["json"]["max_tokens"] <= 32
        assert resp.predicted_answer == "B"
        assert resp.model_id == "Qwen/Qwen3.5-4B"
        assert resp.metadata["rewrite_triggered"] is False
        assert resp.metadata["accepted_draft_ratio"] == 1.0
        assert resp.metadata["verification_steps"][0]["match_strategy"] == "parsed_answer_agreement"


class TestMultiAgentArchitecture:
    def test_all_slm_no_llm_calls(self):
        slm = StubModel("slm", answer="B Final Answer:", confidence=0.8)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = MultiAgentArchitecture(slm=slm, llm=llm, arbitrator="slm")
        resp = arch.run(QUERY)
        assert resp.llm_calls == 0

    def test_llm_arbitrator_counts_call(self):
        slm = StubModel("slm", answer="Critique here", confidence=0.7)
        llm = StubModel("llm", answer="B Final Answer:", confidence=0.9)
        arch = MultiAgentArchitecture(slm=slm, llm=llm, arbitrator="llm")
        resp = arch.run(QUERY)
        assert resp.llm_calls == 1

    def test_multi_agent_uses_slm_and_llm_specific_settings(self):
        slm = RecordingStubModel("slm", answer="Answer: B", confidence=0.7)
        llm = RecordingStubModel("llm", answer="B", confidence=0.9)
        arch = MultiAgentArchitecture(
            slm=slm,
            llm=llm,
            arbitrator="llm",
            slm_temperature=0.1,
            llm_temperature=0.8,
            slm_max_tokens=111,
            llm_max_tokens=222,
        )
        arch.run(QUERY)

        assert slm.calls == [
            {"temperature": 0.1, "max_tokens": 111},
            {"temperature": 0.1, "max_tokens": 111},
        ]
        assert llm.calls == [{"temperature": 0.8, "max_tokens": 222}]


class TestEnsembleArchitecture:
    def test_majority_vote_correct(self):
        slm = StubModel("slm", answer="B", confidence=0.85)
        llm = StubModel("llm", answer="C", confidence=0.9)
        arch = EnsembleArchitecture(slm=slm, llm=llm, n_models=3, voting="majority")
        resp = arch.run(QUERY)
        assert resp.predicted_answer == "B"
        assert resp.llm_calls == 0
        assert len(resp.metadata["ensemble_member_responses"]) == 3
        assert resp.metadata["ensemble_member_responses"][0]["raw_text"] == "B"
        assert resp.metadata["ensemble_member_responses"][0]["parsed_answer"] == "B"
        assert resp.metadata["final_answer_source"] == "ensemble_vote"

    def test_no_majority_with_llm_tiebreak(self):
        # 3 models all return different answers — simulate by patching
        answers = iter(["A", "B", "C"])
        slm = MagicMock(spec=ModelProvider)
        slm.model_id = "slm"
        slm.generate.side_effect = lambda p, **k: (next(answers), 0.6, 5, 3, 0.0)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = EnsembleArchitecture(
            slm=slm, llm=llm, n_models=3, voting="majority", llm_tiebreak=True
        )
        resp = arch.run(QUERY)
        assert resp.llm_calls == 1
        assert resp.metadata["llm_tiebreak_raw_text"] == "B"
        assert resp.metadata["llm_tiebreak_parsed_answer"] == "B"
        assert resp.metadata["final_answer_source"] == "llm_tiebreak"

    def test_ensemble_uses_slm_and_llm_specific_settings(self):
        slm = SequenceRecordingStubModel("slm", answers=["A", "B"], confidence=0.85)
        llm = RecordingStubModel("llm", answer="B", confidence=0.9)
        arch = EnsembleArchitecture(
            slm=slm,
            llm=llm,
            n_models=2,
            voting="majority",
            llm_tiebreak=True,
            slm_temperature=0.25,
            llm_temperature=0.55,
            slm_max_tokens=144,
            llm_max_tokens=377,
        )
        arch.run(QUERY)

        assert slm.calls == [
            {"temperature": 0.25, "max_tokens": 144},
            {"temperature": 0.25, "max_tokens": 144},
        ]
        assert llm.calls == [{"temperature": 0.55, "max_tokens": 377}]

    def test_ensemble_exposes_member_generation_metadata(self):
        slm = MetadataStubModel(
            "slm",
            answer="Answer: B",
            confidence=0.85,
            finish_reason="length",
            effective_max_tokens=660,
        )
        arch = EnsembleArchitecture(slm=slm, n_models=1, voting="majority")

        resp = arch.run(QUERY)

        member = resp.metadata["ensemble_member_responses"][0]
        assert member["finish_reason"] == "length"
        assert member["effective_max_tokens"] == 660

    def test_ensemble_runs_distinct_members_in_parallel(self):
        members = [
            SlowStubModel("slm_a", answer="B", confidence=0.8, delay_s=0.15),
            SlowStubModel("slm_b", answer="B", confidence=0.8, delay_s=0.15),
            SlowStubModel("slm_c", answer="B", confidence=0.8, delay_s=0.15),
        ]
        arch = EnsembleArchitecture(slms=members, voting="majority")

        started = time.perf_counter()
        resp = arch.run(QUERY)
        elapsed_s = time.perf_counter() - started

        assert resp.predicted_answer == "B"
        assert elapsed_s < 0.32
        assert resp.latency_ms < 320
        assert [member["model_id"] for member in resp.metadata["ensemble_member_responses"]] == [
            "slm_a",
            "slm_b",
            "slm_c",
        ]


class TestActiveOracleArchitecture:
    def test_oracle_loop_calls_llm_and_returns_final_answer(self):
        slm = SequenceRecordingStubModel(
            "slm",
            answers=["CALL_ORACLE: What is 2+2?", "Final Answer: B"],
            confidence=0.85,
        )
        llm = RecordingStubModel("llm", answer="4", confidence=0.9)
        arch = ActiveOracleArchitecture(slm=slm, llm=llm, max_oracle_calls=2)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 1
        assert resp.predicted_answer == "B"
        assert resp.metadata["oracle_calls_made"] == 1
        assert resp.metadata["oracle_queries"][0] == "What is 2+2?"

class TestEATSMetric:
    def test_lower_resource_penalty_gives_higher_eats(self):
        from evaluation.metrics import compute_eats

        eats_efficient = compute_eats(
            accuracy=0.75,
            normalized_cost=0.3,
            normalized_algorithmic_latency=0.4,
            normalized_energy=0.5,
        )
        eats_expensive = compute_eats(
            accuracy=0.80,
            normalized_cost=1.5,
            normalized_algorithmic_latency=1.4,
            normalized_energy=1.3,
        )
        assert eats_efficient > eats_expensive


class BlackboardStubModel(ModelProvider):
    """A specialized stub model to simulate Blackboard swarm behaviors."""
    def __init__(self, model_id: str, behavior: str, confidence: float = 0.9):
        super().__init__(model_id)
        self.behavior = behavior
        self.confidence = confidence

    def generate(self, prompt: str, **kwargs):
        # 1. Bidding Phase: The architecture checks confidence with max_tokens=1
        if kwargs.get("max_tokens") == 1:
            return "bid_token", self.confidence, 1, 1, 0.0
            
        # 2. Execution Phase: Simulate different swarm outcomes
        if self.behavior == "sweeper":
            return "B", self.confidence, 10, 5, 0.0
            
        if self.behavior == "direct":
            return "B", self.confidence, 10, 5, 0.0
            
        if self.behavior == "subtask":
            # If it's a sub-task prompt, resolve it
            if "Resolve this localized blocker" in prompt:
                return "sub-answer-resolved", self.confidence, 10, 5, 0.0
            # If the dependencies are resolved, output the final answer
            elif "Resolved parameters" in prompt:
                return "B", self.confidence, 10, 5, 0.0
            # Otherwise, get "stuck" and generate a sub-task
            else:
                return "I am stuck. SUB_TASK: what is X?", self.confidence, 10, 5, 0.0

        return "B", self.confidence, 10, 5, 0.0


class RecordingBlackboardStub(BlackboardStubModel):
    """Counts how many bid probes (max_tokens == 1) the worker issues."""

    def __init__(self, model_id: str, behavior: str, confidence: float = 0.9):
        super().__init__(model_id, behavior, confidence)
        self.bid_calls = 0

    def generate(self, prompt: str, **kwargs):
        if kwargs.get("max_tokens") == 1:
            self.bid_calls += 1
        return super().generate(prompt, **kwargs)


class FailingExecStubModel(ModelProvider):
    """Bids fine (max_tokens == 1) but raises on any real execution call."""

    def __init__(self, model_id: str, confidence: float = 0.9):
        super().__init__(model_id)
        self.confidence = confidence

    def generate(self, prompt: str, **kwargs):
        if kwargs.get("max_tokens") == 1:
            return "bid_token", self.confidence, 1, 1, 0.0
        raise RuntimeError("simulated endpoint failure")


class TestBlackboardArchitecture:
    
    def test_slm_claims_and_resolves_fast(self):
        """Test that high-confidence SLMs resolve tasks without the LLM."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture
        
        slm1 = BlackboardStubModel("slm_primary", behavior="direct", confidence=0.9)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.1)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)
        
        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm)
        resp = arch.run(QUERY)
        
        assert resp.llm_calls == 0
        assert resp.predicted_answer == "B"
        assert resp.model_id == "PrimarySLM"

    def test_heavy_sweeper_triggers_on_low_bids(self):
        """Test that the 70B model intervenes if all SLMs bid too low."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture
        
        # Both SLMs lack confidence and ignore the task
        slm1 = BlackboardStubModel("slm_primary", behavior="direct", confidence=0.1)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.1)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)
        
        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm)
        resp = arch.run(QUERY)
        
        # The TTL should expire (~0.6s) and the heavy sweeper picks it up
        assert resp.llm_calls == 1
        assert resp.predicted_answer == "B"
        assert resp.model_id == "HeavySweeper70B"

    def test_subtask_dependency_resolution(self):
        """Test the Active Oracle pattern where SLMs generate and resolve sub-tasks."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture
        
        # Primary SLM is programmed to get stuck and issue a SUB_TASK
        slm1 = BlackboardStubModel("slm_primary", behavior="subtask", confidence=0.9)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.1)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)
        
        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm)
        resp = arch.run(QUERY)
        
        assert resp.llm_calls == 0
        assert resp.predicted_answer == "B"
        
        # Verify the inference steps reflect the sub-tasking loop
        steps = resp.metadata["inference_steps"]
        assert len(steps) >= 3 # 1. Main task blocks, 2. Sub-task resolves, 3. Main task resumes

    def test_run_does_not_hang_when_workers_fail(self):
        """A failing worker re-routes to the sweeper; retries cap → best-effort."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        slm1 = FailingExecStubModel("slm_primary", confidence=0.9)
        slm2 = FailingExecStubModel("slm_secondary", confidence=0.9)
        llm = FailingExecStubModel("llm_sweeper", confidence=0.9)

        arch = DecentralizedBlackboardArchitecture(
            slm1, slm2, llm, ttl_ms=50, max_task_attempts=2
        )
        resp = arch.run(QUERY)  # must return rather than hang forever

        # Exhausted retries → best-effort empty resolution, no crash.
        assert resp is not None
        assert resp.predicted_answer is None
        error_steps = [s for s in resp.metadata["inference_steps"] if s.get("role") == "error"]
        assert error_steps  # failures were recorded for observability

    def test_bids_are_accounted_in_inference_steps(self):
        """Bid probes are recorded as role='bid' steps and counted in totals."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        slm1 = BlackboardStubModel("slm_primary", behavior="direct", confidence=0.9)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.1)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)

        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm)
        resp = arch.run(QUERY)

        bid_steps = [s for s in resp.metadata["inference_steps"] if s.get("role") == "bid"]
        assert bid_steps  # bidding overhead is visible to energy accounting
        assert all("model_id" in s and "latency_ms" in s for s in bid_steps)
        assert resp.input_tokens > 0  # bid + execution tokens folded into totals

    def test_bid_is_computed_once_per_task(self):
        """Caching: each worker bids once per task despite many polling ticks."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        # Both SLMs bid too low to claim, so the root stays OPEN for the whole
        # TTL window (~6 ticks at 50ms) before the sweeper takes it. Without
        # caching each worker would re-bid every tick.
        slm1 = RecordingBlackboardStub("slm_primary", behavior="direct", confidence=0.1)
        slm2 = RecordingBlackboardStub("slm_secondary", behavior="direct", confidence=0.1)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)

        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm, ttl_ms=300)
        resp = arch.run(QUERY)

        assert resp.model_id == "HeavySweeper70B"
        assert resp.llm_calls == 1
        assert slm1.bid_calls == 1
        assert slm2.bid_calls == 1

    def test_highest_bidder_wins_not_first_polled(self):
        """Auction: the secondary wins when it outbids the (first-polled) primary."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        # Primary bid ~0.6985, secondary bid ~0.987 — both clear 0.65, secondary
        # is higher. Under first_threshold the primary would steal it by polling
        # order; under the default highest_bid auction the secondary must win.
        slm1 = BlackboardStubModel("slm_primary", behavior="direct", confidence=0.70)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.99)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)

        # Pin the threshold so the test exercises the claim policy, not the
        # default bid_threshold — both bids (0.6985, 0.987) must clear it.
        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm, bid_threshold=0.65)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id == "SecondarySLM"
        assert resp.metadata["final_model_id"] == "slm_secondary"

    def test_first_threshold_policy_keeps_primary_priority(self):
        """Legacy policy: the first-polled eligible worker (primary) claims."""
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        # Same bids as above, but with the legacy policy the primary wins despite
        # the secondary's higher bid.
        slm1 = BlackboardStubModel("slm_primary", behavior="direct", confidence=0.70)
        slm2 = BlackboardStubModel("slm_secondary", behavior="direct", confidence=0.99)
        llm = BlackboardStubModel("llm_sweeper", behavior="sweeper", confidence=0.9)

        arch = DecentralizedBlackboardArchitecture(
            slm1, slm2, llm, claim_policy="first_threshold", bid_threshold=0.65
        )
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id == "PrimarySLM"

    def test_slow_eligible_bid_not_preempted_by_sweeper(self):
        """A bid that takes longer than the TTL must still win, not be swept.

        Reproduces the 'ghost escalation' bug: on a busy GPU a bid's wall time
        can exceed ttl_ms; the sweeper must wait for the SLMs to actually bid
        (and decline) instead of racing a fixed timer.
        """
        import time as _time
        from architectures.blackboard import DecentralizedBlackboardArchitecture

        class SlowBidStub(ModelProvider):
            def __init__(self, model_id: str, conf: float):
                super().__init__(model_id)
                self.conf = conf

            def generate(self, prompt: str, **kwargs):
                if kwargs.get("max_tokens") == 1:
                    _time.sleep(0.3)  # bid wall time >> ttl_ms below
                    return "x", self.conf, 1, 1, 0.0
                return "B", self.conf, 10, 5, 0.0

        slm1 = SlowBidStub("slm_primary", 0.99)    # bid ~0.988 ≥ 0.8 → eligible
        slm2 = SlowBidStub("slm_secondary", 0.99)
        llm = SlowBidStub("llm_sweeper", 0.9)

        # ttl is 100ms but each bid takes 300ms; the old timer-based sweeper would
        # steal the task before the bids return.
        arch = DecentralizedBlackboardArchitecture(slm1, slm2, llm, ttl_ms=100)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id in ("PrimarySLM", "SecondarySLM")


class TestSwarmAndBlackboardPromptWrapping:
    def test_pure_swarm_prompt_wrapping(self, monkeypatch):
        from architectures.pure_swarm import PureSwarmArchitecture, SwarmTask
        
        slm = RecordingStubModel("slm", answer="B", confidence=0.9)
        arch = PureSwarmArchitecture(slm=slm, secondary_slm=slm, max_subtasks=1)
        
        # 1. Test when can_spawn is True
        task_can_spawn = SwarmTask(
            id="task_root",
            type="main_query",
            prompt="Final Problem Text.",
            subtask_spawned=0,
        )
        
        captured_prompt = ""
        def fake_timed_generate(provider, prompt, **kwargs):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "B", 0.9, 10, 5, 0.0, 1.0
            
        monkeypatch.setattr(arch, "_timed_generate", fake_timed_generate)
        
        import asyncio
        asyncio.run(arch._execute_task("worker1", slm, task_can_spawn, {}))
        
        assert "SUB_TASK:" in captured_prompt
        assert "You MUST solve the problem step-by-step." in captured_prompt
        
        # 2. Test when can_spawn is False (subtask limit reached)
        task_cannot_spawn = SwarmTask(
            id="task_root",
            type="main_query",
            prompt="Final Problem Text.",
            subtask_spawned=1,
        )
        
        asyncio.run(arch._execute_task("worker1", slm, task_cannot_spawn, {}))
        
        assert "SUB_TASK:" not in captured_prompt
        assert "Solve the problem step-by-step and provide the final answer." in captured_prompt

    def test_pure_swarm_nested_subtasks_blocking(self, monkeypatch):
        import asyncio

        from architectures.pure_swarm import PureSwarmArchitecture, SwarmTask

        captured_prompt = ""
        def fake_timed_generate(provider, prompt, **kwargs):
            nonlocal captured_prompt
            captured_prompt = prompt
            return "SUB_TASK: solve subtask", 0.9, 10, 5, 0.0, 1.0

        slm = RecordingStubModel("slm", answer="SUB_TASK: solve sub-sub task", confidence=0.9)
        
        # 1. With allow_nested_subtasks=False (Default): should NOT spawn sub-sub-task
        arch_default = PureSwarmArchitecture(slm=slm, secondary_slm=slm, max_subtasks=2, allow_nested_subtasks=False)
        monkeypatch.setattr(arch_default, "_timed_generate", fake_timed_generate)
        subtask_1 = SwarmTask(
            id="sub_task_123",
            type="sub_probe",
            prompt="Find factorials",
            subtask_spawned=0,
        )
        
        blackboard = {}
        asyncio.run(arch_default._execute_task("worker1", slm, subtask_1, blackboard))
        # Should not spawn nested subtask because allow_nested_subtasks=False
        assert subtask_1.subtask_spawned == 0
        assert "final_output" in subtask_1.results
        assert len(blackboard) == 0
        # Verification that prompt was formatted to solve directly
        assert "SUB_TASK:" not in captured_prompt
        assert "Solve the problem step-by-step and provide the final answer." in captured_prompt

        # 2. With allow_nested_subtasks=True: should spawn nested sub-sub-task
        arch_nested = PureSwarmArchitecture(slm=slm, secondary_slm=slm, max_subtasks=2, allow_nested_subtasks=True)
        monkeypatch.setattr(arch_nested, "_timed_generate", fake_timed_generate)
        subtask_2 = SwarmTask(
            id="sub_task_123",
            type="sub_probe",
            prompt="Find factorials",
            subtask_spawned=0,
        )
        
        blackboard = {}
        # Avoid blocking on asyncio.create_task by mocking _await_dependencies_and_resume
        async def fake_await(t, bb):
            pass
        monkeypatch.setattr(arch_nested, "_await_dependencies_and_resume", fake_await)
        
        asyncio.run(arch_nested._execute_task("worker1", slm, subtask_2, blackboard))
        # Should spawn nested subtask because allow_nested_subtasks=True
        assert subtask_2.subtask_spawned == 1
        assert "final_output" not in subtask_2.results
        assert len(blackboard) == 1
        # Verification that prompt was formatted to allow subtasks
        assert "SUB_TASK: <query>" in captured_prompt
        assert "You MUST solve the problem step-by-step." in captured_prompt


def _entropy_fake_post(distribution: list[dict]):
    """Build a fake OpenAI-compatible response whose single output token carries
    the given top_logprobs distribution."""

    class FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload
            self.status_code = 200
            self.headers = {}

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_post(url, json, headers, timeout):
        return FakeResponse({
            "choices": [
                {
                    "message": {"content": "B"},
                    "logprobs": {
                        "content": [
                            {
                                "token": distribution[0]["token"],
                                "logprob": distribution[0]["logprob"],
                                "top_logprobs": distribution,
                            }
                        ]
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 1},
        })

    return fake_post


class TestTokenEntropy:
    def test_uniform_distribution_yields_max_entropy(self, monkeypatch):
        import math

        from core.models import OpenAICompatibleModel

        uniform = [{"token": t, "logprob": math.log(0.25)} for t in ["A", "B", "C", "D"]]
        monkeypatch.setattr("core.models.requests.post", _entropy_fake_post(uniform))
        model = OpenAICompatibleModel("test/model", base_url="http://localhost:8000/v1")
        model.generate("Question?", max_tokens=1, top_logprobs=4)

        assert abs(model.last_generation_metadata["mean_token_entropy_norm"] - 1.0) < 1e-6

    def test_peaked_distribution_yields_low_entropy(self, monkeypatch):
        import math

        from core.models import OpenAICompatibleModel

        peaked = [
            {"token": "B", "logprob": math.log(0.97)},
            {"token": "A", "logprob": math.log(0.01)},
            {"token": "C", "logprob": math.log(0.01)},
            {"token": "D", "logprob": math.log(0.01)},
        ]
        monkeypatch.setattr("core.models.requests.post", _entropy_fake_post(peaked))
        model = OpenAICompatibleModel("test/model", base_url="http://localhost:8000/v1")
        model.generate("Question?", max_tokens=1, top_logprobs=4)

        assert model.last_generation_metadata["mean_token_entropy_norm"] < 0.2

    def test_default_top_logprobs_skips_entropy(self, monkeypatch):
        import math

        from core.models import OpenAICompatibleModel

        single = [{"token": "B", "logprob": math.log(0.9)}]
        monkeypatch.setattr("core.models.requests.post", _entropy_fake_post(single))
        model = OpenAICompatibleModel("test/model", base_url="http://localhost:8000/v1")
        model.generate("Question?", max_tokens=1)  # default top_logprobs=1 → no-op

        assert "mean_token_entropy_norm" not in model.last_generation_metadata


class EntropyStub(ModelProvider):
    """Bid probes (top_logprobs > 1) expose a normalized entropy; execution
    calls (default top_logprobs) return a fixed answer."""

    def __init__(self, model_id: str, h_norm: float | None, confidence: float = 0.9, answer: str = "B"):
        super().__init__(model_id)
        self.h_norm = h_norm
        self.confidence = confidence
        self.answer = answer

    def generate(self, prompt: str, **kwargs):
        if int(kwargs.get("top_logprobs", 1)) > 1:
            self.last_generation_metadata = (
                {} if self.h_norm is None else {"mean_token_entropy_norm": self.h_norm}
            )
            return "bid_token", self.confidence, 1, 1, 0.0
        return self.answer, self.confidence, 10, 5, 0.0


class TestEntropyBlackboardArchitecture:
    def test_low_entropy_slm_claims_without_sweeper(self):
        from architectures.entropy_based_blackboard import (
            DecentralizedBlackboardArchitecture as Entropy,
        )

        slm1 = EntropyStub("slm_primary", h_norm=0.0, confidence=0.9)
        slm2 = EntropyStub("slm_secondary", h_norm=0.0, confidence=0.1)
        llm = EntropyStub("llm_sweeper", h_norm=0.0, confidence=0.9)

        arch = Entropy(slm1, slm2, llm, entropy_weight=0.5)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id == "PrimarySLM"
        assert resp.predicted_answer == "B"

    def test_high_entropy_defers_to_sweeper(self):
        from architectures.entropy_based_blackboard import (
            DecentralizedBlackboardArchitecture as Entropy,
        )

        # confidence 0.9 but H_norm 1.0 → bid 0.9 - 0.5*1.0 - ~0 = 0.4 < 0.65,
        # so no SLM claims and the TTL hands the task to the heavy sweeper.
        slm1 = EntropyStub("slm_primary", h_norm=1.0, confidence=0.9)
        slm2 = EntropyStub("slm_secondary", h_norm=1.0, confidence=0.9)
        llm = EntropyStub("llm_sweeper", h_norm=1.0, confidence=0.9)

        arch = Entropy(slm1, slm2, llm, entropy_weight=0.5, ttl_ms=100)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 1
        assert resp.model_id == "HeavySweeper70B"

    def test_missing_distribution_falls_back_to_confidence(self):
        from architectures.entropy_based_blackboard import (
            DecentralizedBlackboardArchitecture as Entropy,
        )

        # Provider exposes no entropy → bid reduces to the confidence proxy, so a
        # confident primary still claims the task.
        slm1 = EntropyStub("slm_primary", h_norm=None, confidence=0.9)
        slm2 = EntropyStub("slm_secondary", h_norm=None, confidence=0.1)
        llm = EntropyStub("llm_sweeper", h_norm=None, confidence=0.9)

        arch = Entropy(slm1, slm2, llm, entropy_weight=0.5)
        resp = arch.run(QUERY)

        assert resp.llm_calls == 0
        assert resp.model_id == "PrimarySLM"
