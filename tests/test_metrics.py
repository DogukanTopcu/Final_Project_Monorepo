"""Tests for evaluation metrics, especially EATS."""
from evaluation.metrics import compute_eats, compute_metrics
from core.types import ExperimentConfig, ExperimentResult, SampleResult, Query, Response


def make_result(n: int = 10, n_correct: int = 7, llm_calls_each: int = 0) -> ExperimentResult:
    cfg = ExperimentConfig(architecture="routing", benchmark="mmlu")
    result = ExperimentResult(experiment_id="test_exp", config=cfg)
    for i in range(n):
        q = Query(id=f"q{i}", text="test", answer="A")
        r = Response(
            query_id=f"q{i}",
            text="A",
            predicted_answer="A" if i < n_correct else "B",
            llm_calls=llm_calls_each,
            latency_ms=50.0,
            algorithmic_latency_ms=40.0,
            cost_usd=0.001 * llm_calls_each,
            energy_kwh=0.01 * max(llm_calls_each, 1),
            co2_g=1.0 * max(llm_calls_each, 1),
        )
        result.samples.append(SampleResult(query=q, response=r, correct=(i < n_correct)))
    return result


def test_eats_pure_slm():
    # penalty = 0.5*1 + 0.3*1 + 0.2*1 = 1.0  →  eats = 0.7 / (0.7 + 1.0)
    eats = compute_eats(accuracy=0.70)
    assert 0.0 < eats < 1.0
    assert abs(eats - (0.70 / (0.70 + 1.0))) < 1e-6


def test_eats_full_llm():
    # Same penalty = 1.0  →  eats = 0.8 / (0.8 + 1.0)
    eats = compute_eats(
        accuracy=0.80,
        normalized_cost=1.0,
        normalized_algorithmic_latency=1.0,
        normalized_energy=1.0,
    )
    assert abs(eats - (0.80 / (0.80 + 1.0))) < 1e-6


def test_eats_higher_for_efficient_system():
    efficient = compute_eats(
        accuracy=0.72,
        normalized_cost=0.2,
        normalized_algorithmic_latency=0.3,
        normalized_energy=0.4,
    )
    expensive = compute_eats(
        accuracy=0.75,
        normalized_cost=1.5,
        normalized_algorithmic_latency=1.4,
        normalized_energy=1.3,
    )
    assert efficient > expensive


def test_compute_metrics_structure():
    result = make_result(n=10, n_correct=8, llm_calls_each=0)
    metrics = compute_metrics(result)
    assert "accuracy" in metrics
    assert "eats_score" in metrics
    assert "llm_call_ratio" in metrics
    assert "avg_algorithmic_latency_ms" in metrics
    assert "normalized_algorithmic_latency" in metrics
    assert "normalized_energy" in metrics
    assert "normalized_efficiency_penalty" in metrics
    assert abs(metrics["accuracy"] - 0.8) < 1e-6


def test_accuracy_and_llm_ratio():
    result = make_result(n=10, n_correct=7, llm_calls_each=1)
    assert abs(result.accuracy - 0.7) < 1e-6
    assert abs(result.llm_call_ratio - 1.0) < 1e-6


def test_compute_metrics_normalizes_all_resource_terms():
    result = make_result(n=10, n_correct=8, llm_calls_each=1)
    metrics = compute_metrics(
        result,
        full_llm_cost_usd=0.02,
        full_llm_avg_algorithmic_latency_ms=80.0,
        full_llm_energy_kwh=0.2,
    )
    assert abs(metrics["normalized_cost"] - 0.5) < 1e-6
    assert abs(metrics["normalized_algorithmic_latency"] - 0.5) < 1e-6
    assert abs(metrics["normalized_energy"] - 0.5) < 1e-6
    assert abs(metrics["normalized_efficiency_penalty"] - 0.5) < 1e-6
    # penalty = 0.5*0.5 + 0.3*0.5 + 0.2*0.5 = 0.5  →  eats = 0.8 / (0.8 + 0.5)
    assert abs(metrics["eats_score"] - (0.8 / (0.8 + 0.5))) < 1e-6


def test_higher_latency_and_energy_reduce_eats():
    efficient = compute_eats(
        accuracy=0.75,
        normalized_cost=1.0,
        normalized_algorithmic_latency=0.5,
        normalized_energy=0.5,
    )
    wasteful = compute_eats(
        accuracy=0.75,
        normalized_cost=1.0,
        normalized_algorithmic_latency=2.0,
        normalized_energy=2.0,
    )
    assert efficient > wasteful


def test_algorithmic_latency_defaults_to_inference_steps_sum():
    response = Response(
        query_id="q0",
        text="A",
        predicted_answer="A",
        latency_ms=90.0,
        metadata={
            "inference_steps": [
                {"latency_ms": 10.0},
                {"latency_ms": 15.0},
            ]
        },
    )
    result = ExperimentResult(
        experiment_id="test_exp_steps",
        config=ExperimentConfig(architecture="routing", benchmark="mmlu"),
        samples=[SampleResult(query=Query(id="q0", text="x", answer="A"), response=response, correct=True)],
    )
    metrics = compute_metrics(result)
    assert abs(metrics["avg_latency_ms"] - 90.0) < 1e-6
    assert abs(metrics["avg_algorithmic_latency_ms"] - 25.0) < 1e-6
