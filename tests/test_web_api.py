from __future__ import annotations

from contextlib import nullcontext
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core.model_catalog import SELECTED_MODELS
from evaluation.reporter import Reporter
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
    assert benchmark_ids == {
        "mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa",
        "humaneval_plus", "livecodebench",
        "custom_stratified",
    }


def test_models_endpoint_lists_selected_remote_models(client: TestClient, monkeypatch):
    from web.backend.routers import models as models_router

    async def fake_probe(provider: str, base_url: str, timeout: float = 1.5):
        return True, None

    monkeypatch.setattr(models_router, "_probe_runtime_endpoint", fake_probe)
    monkeypatch.setattr(
        models_router,
        "fetch_served_model_ids",
        lambda base_url: {
            "Qwen/Qwen3.5-4B",
            "openai/gpt-oss-20b",
            "meta-llama/Llama-3.3-70B-Instruct",
        },
    )
    response = client.get("/api/models")
    assert response.status_code == 200

    payload = response.json()
    assert {model["id"] for model in payload["slm"]} == {
        spec.id for spec in SELECTED_MODELS if spec.kind == "slm"
    }
    assert {model["id"] for model in payload["llm"]} == {
        spec.id for spec in SELECTED_MODELS if spec.kind == "llm"
    }
    assert payload["warnings"] == []
    qwen = next(model for model in payload["slm"] if model["id"] == "qwen3.5-4b")
    assert qwen["configured"] is True
    assert qwen["is_active_on_host"] is None


def test_runtime_provider_env_is_synced_from_settings(monkeypatch):
    monkeypatch.delenv("THESIS_GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = get_settings()
    settings.gemini_api_key = "gemini-test-key"

    experiment_service._sync_runtime_provider_env(settings)  # type: ignore[attr-defined]

    assert os.getenv("THESIS_GEMINI_API_KEY") == "gemini-test-key"
    assert os.getenv("GEMINI_API_KEY") == "gemini-test-key"


def test_launch_accepts_ensemble_architecture(client: TestClient):
    response = client.post(
        "/api/experiments",
        json={
            "architecture": "ensemble",
            "benchmark": "mmlu",
            "n_samples": 5,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {"dry_run": True},
        },
    )

    assert response.status_code == 200


def test_launch_accepts_active_oracle_architecture(client: TestClient):
    response = client.post(
        "/api/experiments",
        json={
            "architecture": "active_oracle",
            "benchmark": "mmlu",
            "n_samples": 5,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {"dry_run": True, "max_oracle_calls": 2},
        },
    )

    assert response.status_code == 200


def test_launch_accepts_rtos_watchdog_architecture(client: TestClient):
    response = client.post(
        "/api/experiments",
        json={
            "architecture": "rtos_watchdog",
            "benchmark": "mmlu",
            "n_samples": 5,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {"dry_run": True, "confidence_threshold": 0.55},
        },
    )

    assert response.status_code == 200


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
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
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


def test_launch_accepts_per_model_runtime_settings(client: TestClient, monkeypatch):
    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 3,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {
                "dry_run": True,
                "slm_temperature": 0.15,
                "llm_temperature": 0.55,
                "slm_max_tokens": 512,
                "llm_max_tokens": 2048,
            },
        },
    )

    assert response.status_code == 200
    experiment_id = response.json()["experiment_id"]

    queued = client.get(f"/api/experiments/{experiment_id}")
    assert queued.status_code == 200
    payload = queued.json()
    assert payload["config_overrides"]["slm_temperature"] == 0.15
    assert payload["config_overrides"]["llm_temperature"] == 0.55
    assert payload["config_overrides"]["slm_max_tokens"] == 512
    assert payload["config_overrides"]["llm_max_tokens"] == 2048


def test_launch_rejects_unsupported_override_keys(client: TestClient, monkeypatch):
    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 3,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {
                "slm_only": True,
                "dry_run": False,
            },
        },
    )

    assert response.status_code == 400


def test_launch_rejects_invalid_runtime_setting_ranges(client: TestClient):
    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 3,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {"slm_temperature": 2.5},
        },
    )

    assert response.status_code == 400
    assert "slm_temperature" in response.json()["detail"]


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
                    model_id="qwen3.5-4b",
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
                            model_id="gpt-oss-20b",
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
    monkeypatch.setattr(experiment_service, "reserve_llm_host", lambda *args, **kwargs: nullcontext())

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "arc",
            "n_samples": 1,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
            "config_overrides": {"confidence_threshold": 0.7},
        },
    )
    assert response.status_code == 200
    experiment_id = response.json()["experiment_id"]

    fn, args, kwargs = executor.tasks.pop()
    fn(*args, **kwargs)

    events = experiment_service.get_events(experiment_id)
    event_types = [event["type"] for event in events]
    assert "progress" in event_types
    assert event_types.count("metric") == 2
    assert event_types[-1] == "complete"
    assert "total_cost_usd" in events[-1]["metrics"]
    assert "eats_score" in events[-1]["metrics"]

    results = client.get("/api/results")
    assert results.status_code == 200
    result_payload = results.json()
    matching = next(item for item in result_payload if item["experiment_id"] == experiment_id)
    assert matching["total_cost_usd"] == pytest.approx(0.01)
    assert matching["eats_score"] > 0


def test_get_result_returns_routing_audit_samples(client: TestClient, tmp_path: Path):
    result = ExperimentResult(
        experiment_id="exp_audit_detail",
        config=experiment_service._build_config(  # type: ignore[attr-defined]
            create_stub_params(llm="gemini-2.5-flash"),
            get_settings(),
        ),
        samples=[
            SampleResult(
                query=Query(id="q1", text="Question 1", answer="B"),
                response=Response(
                    query_id="q1",
                    text="B",
                    predicted_answer="B",
                    confidence=0.4,
                    model_id="gemini-2.5-flash",
                    latency_ms=55.0,
                    input_tokens=15,
                    output_tokens=4,
                    cost_usd=0.02,
                    llm_calls=1,
                    metadata={
                        "prompt_text": "Prompt 1",
                        "slm_text": "Draft answer",
                        "final_model_id": "gemini-2.5-flash",
                        "escalated": True,
                        "slm_confidence": 0.4,
                        "confidence_threshold": 0.7,
                        "llm_input_tokens": 10,
                        "llm_output_tokens": 4,
                        "llm_cost_usd": 0.02,
                    },
                ),
                correct=True,
            )
        ],
    )
    Reporter(tmp_path).save(result)

    response = client.get("/api/results/exp_audit_detail")
    assert response.status_code == 200
    payload = response.json()
    sample = payload["samples"][0]
    assert sample["escalated"] is True
    assert sample["final_model_id"] == "gemini-2.5-flash"
    assert sample["prompt_text"] == "Prompt 1"
    assert sample["slm_text"] == "Draft answer"


def test_get_result_gracefully_handles_old_result_shape(client: TestClient, tmp_path: Path):
    old_payload = {
        "experiment_id": "exp_old_shape",
        "created_at": "2026-05-17T12:00:00+00:00",
        "config": {"architecture": "routing", "benchmark": "mmlu"},
        "metrics": {"accuracy": 0.5, "total_cost_usd": 0.0},
        "samples": [
            {
                "query_id": "q1",
                "correct": True,
                "predicted": "A",
                "ground_truth": "A",
                "llm_calls": 0,
                "confidence": 0.9,
                "latency_ms": 10.0,
                "cost_usd": 0.0,
            }
        ],
    }
    (tmp_path / "exp_old_shape.json").write_text(__import__("json").dumps(old_payload))

    response = client.get("/api/results/exp_old_shape")
    assert response.status_code == 200
    sample = response.json()["samples"][0]
    assert sample["query_id"] == "q1"
    assert "final_model_id" not in sample


def test_experiments_endpoint_includes_persisted_local_results(client: TestClient, tmp_path: Path):
    persisted_payload = {
        "experiment_id": "exp_persisted_ui",
        "created_at": "2026-05-19T12:00:00+00:00",
        "config": {
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 5,
            "slm": "qwen3.5-4b",
            "llm": "gpt-oss-20b",
        },
        "metrics": {"accuracy": 0.4, "eats_score": 0.8},
        "samples": [],
    }
    (tmp_path / "exp_persisted_ui.json").write_text(__import__("json").dumps(persisted_payload))

    response = client.get("/api/experiments")
    assert response.status_code == 200
    payload = response.json()
    matching = next(item for item in payload if item["experiment_id"] == "exp_persisted_ui")
    assert matching["status"] == "completed"
    assert matching["metrics"]["accuracy"] == 0.4
    assert matching["slm"] == "qwen3.5-4b"


def test_launch_rejects_unknown_llm_alias(client: TestClient, monkeypatch):
    executor = DeferredExecutor()
    monkeypatch.setattr(experiment_service, "_executor", executor)

    response = client.post(
        "/api/experiments",
        json={
            "architecture": "routing",
            "benchmark": "mmlu",
            "n_samples": 2,
            "slm": "qwen3.5-4b",
            "llm": "gemini-2.5-flash",
            "config_overrides": {"dry_run": False},
        },
    )

    assert response.status_code == 400


def create_stub_params(llm: str = "gpt-oss-20b"):
    from web.backend.schemas import Architecture, Benchmark, ExperimentCreate

    return ExperimentCreate(
        architecture=Architecture.ROUTING,
        benchmark=Benchmark.MMLU,
        n_samples=1,
        slm="qwen3.5-4b",
        llm=llm,
        config_overrides={"confidence_threshold": 0.7},
    )
