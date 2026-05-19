"""Unit tests for architectures — uses a stub ModelProvider (no API calls)."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from core.types import Query, Response
from core.models import ModelProvider
from architectures.routing import RoutingArchitecture
from architectures.multi_agent import MultiAgentArchitecture
from architectures.ensemble import EnsembleArchitecture


class StubModel(ModelProvider):
    """Returns a fixed answer with configurable confidence."""

    def __init__(self, model_id: str, answer: str = "A", confidence: float = 0.9) -> None:
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


QUERY = Query(
    id="q1",
    text="What is 2+2?",
    choices=["3", "4", "5", "6"],
    answer="B",
)


class TestRoutingArchitecture:
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

    def test_unparseable_slm_answer_escalates_even_with_high_confidence(self):
        slm = StubModel("slm", answer="I am not sure", confidence=0.91)
        llm = StubModel("llm", answer="B", confidence=0.9)
        arch = RoutingArchitecture(slm=slm, llm=llm, confidence_threshold=0.7)
        resp = arch.run(QUERY)
        assert resp.llm_calls == 1
        assert resp.model_id == "llm"

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


class TestEATSMetric:
    def test_lower_llm_ratio_gives_higher_eats(self):
        from evaluation.metrics import compute_eats

        eats_efficient = compute_eats(accuracy=0.75, llm_call_ratio=0.1)
        eats_expensive = compute_eats(accuracy=0.80, llm_call_ratio=1.0)
        assert eats_efficient > eats_expensive
