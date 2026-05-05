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
            cost_usd=0.001 * llm_calls_each,
        )
        result.samples.append(SampleResult(query=q, response=r, correct=(i < n_correct)))
    return result


def test_eats_pure_slm():
    eats = compute_eats(accuracy=0.70, llm_call_ratio=0.0)
    assert eats == 0.70 / 0.01  # epsilon=0.01


def test_eats_full_llm():
    eats = compute_eats(accuracy=0.80, llm_call_ratio=1.0, normalized_cost=1.0)
    assert abs(eats - 0.80 / 1.01) < 1e-6


def test_eats_higher_for_efficient_system():
    efficient = compute_eats(accuracy=0.72, llm_call_ratio=0.08)
    expensive = compute_eats(accuracy=0.75, llm_call_ratio=1.0)
    assert efficient > expensive


def test_compute_metrics_structure():
    result = make_result(n=10, n_correct=8, llm_calls_each=0)
    metrics = compute_metrics(result)
    assert "accuracy" in metrics
    assert "eats_score" in metrics
    assert "llm_call_ratio" in metrics
    assert abs(metrics["accuracy"] - 0.8) < 1e-6


def test_accuracy_and_llm_ratio():
    result = make_result(n=10, n_correct=7, llm_calls_each=1)
    assert abs(result.accuracy - 0.7) < 1e-6
    assert abs(result.llm_call_ratio - 1.0) < 1e-6
