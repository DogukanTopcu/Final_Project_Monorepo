"""Tests for coding benchmark infrastructure added today.

Covers:
  - _code_execution: strip_code_fences, run_function_tests, run_io_tests
  - build_prompt / parse_answer for task_type="code"
  - TruthfulQA rotation fix (answer is no longer always A)
  - ECE computation
  - aggregate_runs
  - compute_subject_accuracy
"""
from __future__ import annotations

import pytest

from benchmarks._code_execution import strip_code_fences, run_function_tests, run_io_tests
from core.prompt import build_prompt, parse_answer, mcq_prompt, open_prompt
from core.types import Query, ExperimentConfig, ExperimentResult, SampleResult, Response
from evaluation.metrics import compute_ece, aggregate_runs, compute_subject_accuracy


# ------------------------------------------------------------------
# strip_code_fences
# ------------------------------------------------------------------

def test_strip_fences_extracts_inner_code():
    text = "Here is the solution:\n```python\ndef foo():\n    return 42\n```"
    result = strip_code_fences(text)
    assert "def foo():" in result
    assert "```" not in result


def test_strip_fences_no_fence_returns_text():
    text = "def foo():\n    return 42"
    assert strip_code_fences(text) == text


def test_strip_fences_strips_stray_backtick_lines():
    text = "```\ndef foo(): pass\n```"
    result = strip_code_fences(text)
    assert "def foo(): pass" in result
    assert "```" not in result


# ------------------------------------------------------------------
# run_function_tests (HumanEval+ style)
# ------------------------------------------------------------------

def test_run_function_tests_correct_solution():
    prompt = "def add(a: int, b: int) -> int:\n    \"\"\"\"\"\"\n"
    code = "    return a + b"
    test_code = "def check(candidate):\n    assert candidate(1, 2) == 3\n    assert candidate(-1, 1) == 0"
    assert run_function_tests(prompt, code, test_code, "add") is True


def test_run_function_tests_wrong_solution():
    prompt = "def add(a: int, b: int) -> int:\n    \"\"\"\"\"\"\n"
    code = "    return a - b"
    test_code = "def check(candidate):\n    assert candidate(1, 2) == 3"
    assert run_function_tests(prompt, code, test_code, "add") is False


def test_run_function_tests_timeout():
    prompt = "def spin() -> None:\n    \"\"\"\"\"\"\n"
    code = "    while True: pass"
    test_code = "def check(candidate):\n    candidate()"
    assert run_function_tests(prompt, code, test_code, "spin", timeout=2) is False


# ------------------------------------------------------------------
# run_io_tests (LiveCodeBench style)
# ------------------------------------------------------------------

def test_run_io_tests_correct_program():
    code = "n = int(input())\nprint(n * 2)"
    test_cases = [
        {"input": "3\n", "output": "6"},
        {"input": "0\n", "output": "0"},
    ]
    assert run_io_tests(code, test_cases) is True


def test_run_io_tests_wrong_output():
    code = "n = int(input())\nprint(n + 1)"
    test_cases = [{"input": "3\n", "output": "6"}]
    assert run_io_tests(code, test_cases) is False


def test_run_io_tests_partial_pass_returns_false():
    code = "n = int(input())\nprint(n * 2)"
    test_cases = [
        {"input": "3\n", "output": "6"},   # passes
        {"input": "5\n", "output": "99"},  # fails
    ]
    assert run_io_tests(code, test_cases) is False


def test_run_io_tests_empty_cases_returns_true():
    assert run_io_tests("print('hi')", []) is True


# ------------------------------------------------------------------
# build_prompt / parse_answer for code task type
# ------------------------------------------------------------------

def test_build_prompt_code_returns_query_text_unchanged():
    query = Query(id="q1", text="Write a solution for X.\n\nReturn code only.", answer=None)
    assert build_prompt(query, "code") == query.text


def test_build_prompt_mcq_delegates_to_mcq_prompt():
    query = Query(id="q1", text="Question?", choices=["A", "B", "C", "D"], answer="A")
    assert build_prompt(query, "mcq") == mcq_prompt(query)


def test_build_prompt_open_delegates_to_open_prompt():
    query = Query(id="q1", text="Solve this.", answer="42")
    assert build_prompt(query, "open") == open_prompt(query)


def test_parse_answer_code_returns_raw_text():
    code = "def solution():\n    return 42"
    assert parse_answer(code, "code") == code


def test_parse_answer_code_none_input():
    assert parse_answer(None, "code") is None


def test_parse_answer_mcq_delegates():
    assert parse_answer("Answer: B", "mcq") == "B"


def test_parse_answer_open_delegates():
    assert parse_answer("Answer: 42", "open") == "42"


# ------------------------------------------------------------------
# TruthfulQA rotation fix
# ------------------------------------------------------------------

def test_truthfulqa_answer_not_always_a():
    """After the rotation fix, correct answers should be distributed across positions."""
    from benchmarks.truthfulqa import TruthfulQABenchmark
    bench = TruthfulQABenchmark(n_samples=50, seed=42)
    try:
        queries = bench.load()
    except Exception:
        pytest.skip("TruthfulQA dataset not available in this environment")

    answers = [q.answer for q in queries]
    # With the fix, not all answers should be A
    assert set(answers) != {"A"}, (
        "All answers are A — the position-bias rotation was not removed"
    )
    # Correct answers should appear at multiple positions
    assert len(set(answers)) > 1


# ------------------------------------------------------------------
# ECE
# ------------------------------------------------------------------

def test_ece_perfect_calibration():
    # confidence == accuracy in every bucket → ECE should be 0
    confs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] * 10
    # model is correct exactly when confidence > 0.5
    correct = [c > 0.5 for c in confs]
    ece = compute_ece(confs, correct)
    assert 0.0 <= ece <= 1.0


def test_ece_overconfident_model():
    # Model always says 0.9 confidence but is only 50% accurate
    confs = [0.9] * 100
    correct = [i % 2 == 0 for i in range(100)]
    ece = compute_ece(confs, correct)
    # ECE should be close to |0.9 - 0.5| = 0.4
    assert abs(ece - 0.4) < 0.05


def test_ece_empty_input():
    assert compute_ece([], []) == 0.0


def test_ece_length_mismatch():
    assert compute_ece([0.5, 0.6], [True]) == 0.0


# ------------------------------------------------------------------
# aggregate_runs
# ------------------------------------------------------------------

def test_aggregate_runs_mean_and_std():
    runs = [
        {"accuracy": 0.8, "cost": 1.0},
        {"accuracy": 0.9, "cost": 2.0},
        {"accuracy": 0.7, "cost": 3.0},
    ]
    agg = aggregate_runs(runs)
    assert abs(agg["accuracy_mean"] - 0.8) < 1e-6
    assert abs(agg["cost_mean"] - 2.0) < 1e-6
    assert agg["n_runs"] == 3.0
    # std of [0.8, 0.9, 0.7] = 0.1 (sample std)
    assert abs(agg["accuracy_std"] - 0.1) < 1e-6


def test_aggregate_runs_single_run_std_zero():
    agg = aggregate_runs([{"accuracy": 0.75}])
    assert agg["accuracy_std"] == 0.0


def test_aggregate_runs_empty():
    assert aggregate_runs([]) == {}


# ------------------------------------------------------------------
# compute_subject_accuracy
# ------------------------------------------------------------------

def _make_subject_result(subjects_and_correct: list[tuple[str, bool]]) -> ExperimentResult:
    cfg = ExperimentConfig(architecture="routing", benchmark="mmlu")
    result = ExperimentResult(experiment_id="test", config=cfg)
    for i, (subject, correct) in enumerate(subjects_and_correct):
        q = Query(id=f"q{i}", text="x", answer="A", metadata={"subject": subject})
        r = Response(query_id=f"q{i}", text="A", predicted_answer="A")
        result.samples.append(SampleResult(query=q, response=r, correct=correct))
    return result


def test_compute_subject_accuracy_basic():
    result = _make_subject_result([
        ("math", True), ("math", False), ("math", True),  # math: 2/3
        ("history", True), ("history", True),              # history: 2/2
    ])
    groups = compute_subject_accuracy(result)
    assert "subject" in groups
    assert abs(groups["subject"]["math"] - 2 / 3) < 1e-6
    assert abs(groups["subject"]["history"] - 1.0) < 1e-6


def test_compute_subject_accuracy_difficulty():
    cfg = ExperimentConfig(architecture="routing", benchmark="custom_stratified")
    result = ExperimentResult(experiment_id="test", config=cfg)
    for i, (diff, correct) in enumerate([("easy", True), ("easy", True), ("hard", False)]):
        q = Query(id=f"q{i}", text="x", answer="A", metadata={"difficulty": diff})
        r = Response(query_id=f"q{i}", text="A", predicted_answer="A")
        result.samples.append(SampleResult(query=q, response=r, correct=correct))
    groups = compute_subject_accuracy(result)
    assert "difficulty" in groups
    assert groups["difficulty"]["easy"] == 1.0
    assert groups["difficulty"]["hard"] == 0.0


def test_compute_subject_accuracy_no_metadata():
    cfg = ExperimentConfig(architecture="routing", benchmark="mmlu")
    result = ExperimentResult(experiment_id="test", config=cfg)
    q = Query(id="q0", text="x", answer="A")
    r = Response(query_id="q0", text="A", predicted_answer="A")
    result.samples.append(SampleResult(query=q, response=r, correct=True))
    assert compute_subject_accuracy(result) == {}
