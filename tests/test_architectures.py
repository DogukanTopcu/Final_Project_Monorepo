"""Unit tests for architectures — uses a stub ModelProvider (no API calls)."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from core.types import Query, Response
from core.models import ModelProvider
from architectures.routing import RoutingArchitecture, should_escalate
from architectures.multi_agent import MultiAgentArchitecture
from architectures.ensemble import EnsembleArchitecture
from architectures.active_oracle import ActiveOracleArchitecture
from architectures.rtos_watchdog import RTOSWatchdogArchitecture


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


class TestRTOSWatchdogArchitecture:
    def test_interrupt_triggers_llm_handoff(self, monkeypatch):
        class StreamResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def raise_for_status(self):
                return None

            def iter_lines(self):
                payload = {
                    "choices": [
                        {
                            "delta": {"content": "A"},
                            "logprobs": {"content": [{"logprob": -2.0}]},
                        }
                    ]
                }
                yield f"data: {__import__('json').dumps(payload)}".encode("utf-8")
                yield b"data: [DONE]"

        class StreamSLM(StubModel):
            def __init__(self, model_id: str):
                super().__init__(model_id=model_id, answer="A", confidence=0.9)
                self.base_url = "http://localhost:8001/v1"

        def fake_post(*args, **kwargs):
            return StreamResponse()

        monkeypatch.setattr(
            "architectures.rtos_watchdog.requests.post",
            fake_post,
        )

        slm = StreamSLM("slm")
        llm = RecordingStubModel("llm", answer="B", confidence=0.9)
        arch = RTOSWatchdogArchitecture(
            slm=slm,
            llm=llm,
            confidence_threshold=0.6,
            slm_max_tokens=32,
            llm_max_tokens=32,
        )
        resp = arch.run(QUERY)

        assert resp.llm_calls == 1
        assert resp.metadata["interrupted"] is True


class TestEATSMetric:
    def test_lower_llm_ratio_gives_higher_eats(self):
        from evaluation.metrics import compute_eats

        eats_efficient = compute_eats(accuracy=0.75, llm_call_ratio=0.1)
        eats_expensive = compute_eats(accuracy=0.80, llm_call_ratio=1.0)
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


class TestSwarmAndBlackboardPromptWrapping:
    def test_pure_swarm_prompt_wrapping(self, monkeypatch):
        from architectures.pure_swarm import PureSwarmArchitecture, SwarmTask
        
        slm = RecordingStubModel("slm", answer="B", confidence=0.9)
        arch = PureSwarmArchitecture(slm=slm, secondary_slm=slm, max_subtasks=1)
        
        # 1. Test when can_spawn is True
        task_can_spawn = SwarmTask(
            id="task_root",
            type="main_query",
            prompt="Do not include chain-of-thought or explanation. Final Problem Text.",
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
        
        assert "Do not include chain-of-thought" not in captured_prompt
        assert "SUB_TASK:" in captured_prompt
        assert "You MUST solve the problem step-by-step." in captured_prompt
        
        # 2. Test when can_spawn is False (subtask limit reached)
        task_cannot_spawn = SwarmTask(
            id="task_root",
            type="main_query",
            prompt="Do not include chain-of-thought or explanation. Final Problem Text.",
            subtask_spawned=1,
        )
        
        asyncio.run(arch._execute_task("worker1", slm, task_cannot_spawn, {}))
        
        assert "Do not include chain-of-thought" not in captured_prompt
        assert "SUB_TASK:" not in captured_prompt
        assert "Solve the problem step-by-step and provide the final answer." in captured_prompt
