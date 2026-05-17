from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core.types import ExperimentResult, Query, Response, SampleResult
from web.backend.dependencies import get_settings
from web.backend.main import create_app
from web.backend.services import experiment_service


class DeferredExecutor:
    def __init__(self) -> None:
        self.tasks: list[tuple] = []

    def submit(self, fn, *args, **kwargs):
        self.tasks.append((fn, args, kwargs))
        return None


@pytest.fixture(autouse=True)
def reset_state(monkeypatch, tmp_path: Path):
    experiment_service._experiments.clear()
    experiment_service._cancel_flags.clear()
    experiment_service._sse_queues.clear()

    monkeypatch.setenv("THESIS_RESULTS_DIR", str(tmp_path))
    monkeypatch.delenv("THESIS_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("THESIS_GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("THESIS_TOGETHER_API_KEY", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client(monkeypatch):
    from web.backend.services import aws_service

    monkeypatch.setattr(aws_service, "list_s3_results", lambda bucket: [])
    app = create_app()
    return TestClient(app)


def test_benchmarks_endpoint_matches_active_benchmarks(client: TestClient):
    response = client.get("/api/benchmarks")
    assert response.status_code == 200

    benchmark_ids = {item["id"] for item in response.json()}
    assert benchmark_ids == {"mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa"}


def test_models_endpoint_discovers_local_ollama_models(client: TestClient, monkeypatch):
    from web.backend.routers import models as models_router

    async def fake_fetch(base_url: str):
        return [{"name": "gemma3:4b"}, {"name": "phi3:mini"}]

    monkeypatch.setattr(models_router, "fetch_ollama_tags", fake_fetch)
    response = client.get("/api/models")
    assert response.status_code == 200

    payload = response.json()
    assert payload["ollama_reachable"] is True
    assert [model["id"] for model in payload["slm"]] == ["gemma3:4b", "phi3:mini"]
    assert payload["warnings"] == []
    assert any(model["id"] == "gemini-2.5-flash" for model in payload["llm"])


def test_models_endpoint_handles_unreachable_ollama(client: TestClient, monkeypatch):
    from web.backend.routers import models as models_router

    async def fake_fetch(base_url: str):
        raise RuntimeError("down")

    monkeypatch.setattr(models_router, "fetch_ollama_tags", fake_fetch)
    response = client.get("/api/models")
    assert response.status_code == 200

    payload = response.json()
    assert payload["slm"] == []
    assert payload["ollama_reachable"] is False
    assert payload["warnings"]


def test_launch_rejects_non_routing_architecture(client: TestClient):
    response = client.post(
        "/api/experiments",
        json={
            "architecture": "ensemble",
            "benchmark": "mmlu",
            "n_samples": 5,
            "slm": "gemma3:4b",
            "llm": "gpt-4o-mini",
            "config_overrides": {"dry_run": True},
        },
    )

    assert response.status_code == 400
    assert "routing only" in response.json()["detail"].lower()


def test_launch_dry_run_transitions_to_completed_and_surfaces_metrics(
    client: TestClient,
    monkeypatch,
):
    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 3,
            "slm": "gemma3:4b",
            "llm": "gpt-4o-mini",
            "config_overrides": {"dry_run": True, "confidence_threshold": 0.65},
        },
    )
    assert response.status_code == 200
    experiment_id = response.json()["experiment_id"]

    queued = client.get(f"/api/experiments/{experiment_id}")
    assert queued.status_code == 200
    assert queued.json()["status"] == "queued"

    fn, args, kwargs = executor.tasks.pop()
    fn(*args, **kwargs)

    completed = client.get(f"/api/experiments/{experiment_id}")
    assert completed.status_code == 200
    payload = completed.json()
    assert payload["status"] == "completed"
    assert "eats_score" in payload["metrics"]
    assert "total_cost_usd" in payload["metrics"]


def test_sse_events_and_results_use_real_metric_shape(client: TestClient, monkeypatch):
    monkeypatch.setenv("THESIS_OPENAI_API_KEY", "test-key")
    get_settings.cache_clear()

    class FakeRunner:
        def __init__(self, config, callbacks=None):
            self.config = config
            self.callbacks = callbacks

        def run(self):
            if self.callbacks:
                response = Response(
                    query_id="q1",
                    text="B",
                    predicted_answer="B",
                    confidence=0.82,
                    model_id="gemma3:4b",
                    latency_ms=12.5,
                    input_tokens=4,
                    output_tokens=2,
                    cost_usd=0.01,
                    llm_calls=1,
                )
                self.callbacks.sample_complete(1, 1, response)
                self.callbacks.metric_update("accuracy", 1.0)
                self.callbacks.metric_update("llm_call_ratio", 1.0)
            return ExperimentResult(
                experiment_id="exp_fake_runner",
                config=self.config,
                samples=[
                    SampleResult(
                        query=Query(id="q1", text="Question", choices=["A", "B"], answer="B"),
                        response=Response(
                            query_id="q1",
                            text="B",
                            predicted_answer="B",
                            confidence=0.82,
                            model_id="gpt-4o-mini",
                            latency_ms=12.5,
                            input_tokens=4,
                            output_tokens=2,
                            cost_usd=0.01,
                            llm_calls=1,
                        ),
                        correct=True,
                    )
                ],
            )

    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)
    monkeypatch.setattr(experiment_service, "ExperimentRunner", FakeRunner)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "arc",
            "n_samples": 1,
            "slm": "gemma3:4b",
            "llm": "gpt-4o-mini",
            "config_overrides": {"confidence_threshold": 0.7},
        },
    )
    assert response.status_code == 200
    experiment_id = response.json()["experiment_id"]

    fn, args, kwargs = executor.tasks.pop()
    fn(*args, **kwargs)

    events = experiment_service.get_events(experiment_id)
    assert [event["type"] for event in events] == ["progress", "metric", "metric", "complete"]
    assert "total_cost_usd" in events[-1]["metrics"]
    assert "eats_score" in events[-1]["metrics"]

    results = client.get("/api/results")
    assert results.status_code == 200
    result_payload = results.json()
    matching = next(item for item in result_payload if item["experiment_id"] == experiment_id)
    assert matching["total_cost_usd"] == pytest.approx(0.01)
    assert matching["eats_score"] > 0


def test_launch_accepts_gemini_configured_fallback(client: TestClient, monkeypatch):
    monkeypatch.setenv("THESIS_GEMINI_API_KEY", "gemini-test-key")
    get_settings.cache_clear()

    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 2,
            "slm": "gemma3:4b",
            "llm": "gemini-2.5-flash",
            "config_overrides": {"dry_run": False},
        },
    )

    assert response.status_code == 200
