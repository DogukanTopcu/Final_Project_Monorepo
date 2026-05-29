"""Comprehensive tests for coding benchmark logic.

All tests here are self-contained — no HuggingFace dataset download,
no API calls, no language model. They cover:

  - LiveCodeBench: _normalize_difficulty, _parse_test_cases, is_correct,
    task_type attribute, empty/malformed JSON handling
  - HumanEval+: is_correct with a real Query object, task_type attribute,
    code fence stripping in the full pipeline
  - Both benchmarks: correct task_type="code" flows through build_prompt
    and parse_answer without modification
"""
from __future__ import annotations

import pytest

import benchmarks.livecodebench as livecodebench_module
from benchmarks.humaneval_plus import HumanEvalPlusBenchmark
from benchmarks.livecodebench import (
    LiveCodeBenchBenchmark,
    _files_for_version,
    _normalize_difficulty,
    _parse_test_cases,
)
from core.prompt import build_prompt, parse_answer
from core.types import Query

# ================================================================
# LiveCodeBench — _normalize_difficulty
# ================================================================

class TestNormalizeDifficulty:
    def test_easy_string(self):
        assert _normalize_difficulty("easy") == "easy"

    def test_easy_zero_string(self):
        assert _normalize_difficulty("0") == "easy"

    def test_medium_string(self):
        assert _normalize_difficulty("medium") == "medium"

    def test_medium_one_string(self):
        assert _normalize_difficulty("1") == "medium"

    def test_hard_string(self):
        assert _normalize_difficulty("hard") == "hard"

    def test_hard_two_string(self):
        assert _normalize_difficulty("2") == "hard"

    def test_hard_three_string(self):
        # Codeforces-style high rating bucket
        assert _normalize_difficulty("3") == "hard"

    def test_none_returns_medium(self):
        assert _normalize_difficulty(None) == "medium"

    def test_unexpected_value_returns_medium(self):
        assert _normalize_difficulty("extreme") == "medium"

    def test_mixed_case(self):
        assert _normalize_difficulty("HARD") == "hard"
        assert _normalize_difficulty("Easy") == "easy"


# ================================================================
# LiveCodeBench — _parse_test_cases
# ================================================================

class TestParseTestCases:
    def test_valid_stdin_cases(self):
        raw = '[{"input": "3\\n", "output": "6", "testtype": "stdin"}]'
        cases = _parse_test_cases(raw)
        assert len(cases) == 1
        assert cases[0]["input"] == "3\n"
        assert cases[0]["output"] == "6"

    def test_multiple_cases(self):
        import json
        data = [
            {"input": "1\n", "output": "2", "testtype": "stdin"},
            {"input": "5\n", "output": "10", "testtype": "stdin"},
        ]
        cases = _parse_test_cases(json.dumps(data))
        assert len(cases) == 2

    def test_output_stripped(self):
        raw = '[{"input": "1\\n", "output": "  42  \\n", "testtype": "stdin"}]'
        cases = _parse_test_cases(raw)
        assert cases[0]["output"] == "42"

    def test_empty_testtype_included(self):
        raw = '[{"input": "1\\n", "output": "2", "testtype": ""}]'
        cases = _parse_test_cases(raw)
        assert len(cases) == 1

    def test_expression_type_excluded(self):
        # Expression-based test cases require eval, not stdin/stdout — skip them
        raw = '[{"input": "foo(1)", "output": "2", "testtype": "expression"}]'
        cases = _parse_test_cases(raw)
        assert len(cases) == 0

    def test_mixed_types_only_stdin_kept(self):
        import json
        data = [
            {"input": "1\n", "output": "2", "testtype": "stdin"},
            {"input": "foo()", "output": "3", "testtype": "expression"},
        ]
        cases = _parse_test_cases(json.dumps(data))
        assert len(cases) == 1
        assert cases[0]["input"] == "1\n"

    def test_none_returns_empty(self):
        assert _parse_test_cases(None) == []

    def test_empty_string_returns_empty(self):
        assert _parse_test_cases("") == []

    def test_malformed_json_returns_empty(self):
        assert _parse_test_cases("{not valid json}") == []

    def test_non_list_json_returns_empty(self):
        assert _parse_test_cases('{"input": "1", "output": "2"}') == []


# ================================================================
# LiveCodeBench — version/file mapping and row loading contract
# ================================================================

class TestLiveCodeBenchVersionMapping:
    def test_release_v5_includes_first_five_files(self):
        assert _files_for_version("release_v5") == [
            "test.jsonl",
            "test2.jsonl",
            "test3.jsonl",
            "test4.jsonl",
            "test5.jsonl",
        ]

    def test_release_latest_maps_to_release_v6(self):
        assert _files_for_version("release_latest") == [
            "test.jsonl",
            "test2.jsonl",
            "test3.jsonl",
            "test4.jsonl",
            "test5.jsonl",
            "test6.jsonl",
        ]

    def test_alias_range_maps_to_expected_files(self):
        assert _files_for_version("v3_v5") == [
            "test3.jsonl",
            "test4.jsonl",
            "test5.jsonl",
        ]

    def test_invalid_version_raises_clear_error(self):
        with pytest.raises(ValueError, match="Unsupported LiveCodeBench version_tag"):
            _files_for_version("release_v7")


class TestLiveCodeBenchLoadAll:
    def test_load_all_builds_queries_from_raw_rows(self, monkeypatch: pytest.MonkeyPatch):
        rows = [
            {
                "question_id": "123",
                "question_content": "Double the input integer.",
                "starter_code": "def solve():\n    pass",
                "difficulty": "easy",
                "platform": "codeforces",
                "question_title": "Double It",
                "contest_date": "2024-01-01",
                "public_test_cases": '[{"input": "3\\n", "output": "6", "testtype": "stdin"}]',
            },
            {
                "question_id": "124",
                "question_content": "This row should be skipped.",
                "starter_code": "",
                "difficulty": "hard",
                "platform": "atcoder",
                "question_title": "Skip Me",
                "contest_date": "2024-01-02",
                "public_test_cases": "[]",
            },
        ]
        monkeypatch.setattr(livecodebench_module, "_load_rows", lambda version: rows)

        bench = LiveCodeBenchBenchmark(n_samples=10, seed=42, version="release_v5")
        queries = bench._load_all()

        assert len(queries) == 1
        query = queries[0]
        assert query.id == "lcb_123"
        assert "Double the input integer." in query.text
        assert "Reference starter code" in query.text
        assert query.metadata["difficulty"] == "easy"
        assert query.metadata["title"] == "Double It"
        assert query.metadata["test_cases"] == [{"input": "3\n", "output": "6"}]


# ================================================================
# LiveCodeBench — is_correct (no dataset needed)
# ================================================================

def _lcb_query(test_cases: list[dict]) -> Query:
    """Construct a LiveCodeBench-style Query with test_cases in metadata."""
    return Query(
        id="lcb_test",
        text="Write a program that reads N and prints N*2.",
        answer=None,
        metadata={
            "difficulty": "easy",
            "platform": "codeforces",
            "test_cases": test_cases,
        },
    )


class TestLiveCodeBenchIsCorrect:
    bench = LiveCodeBenchBenchmark.__new__(LiveCodeBenchBenchmark)

    def test_correct_solution(self):
        q = _lcb_query([
            {"input": "3\n", "output": "6"},
            {"input": "0\n", "output": "0"},
        ])
        code = "n = int(input())\nprint(n * 2)"
        assert self.bench.is_correct(code, q) is True

    def test_wrong_solution(self):
        q = _lcb_query([{"input": "3\n", "output": "6"}])
        code = "n = int(input())\nprint(n + 1)"
        assert self.bench.is_correct(code, q) is False

    def test_none_response_is_false(self):
        q = _lcb_query([{"input": "1\n", "output": "2"}])
        assert self.bench.is_correct(None, q) is False

    def test_no_test_cases_is_false(self):
        q = _lcb_query([])
        assert self.bench.is_correct("print('x')", q) is False

    def test_code_inside_fences_is_stripped(self):
        q = _lcb_query([{"input": "4\n", "output": "8"}])
        code = "```python\nn = int(input())\nprint(n * 2)\n```"
        assert self.bench.is_correct(code, q) is True

    def test_task_type_is_code(self):
        assert LiveCodeBenchBenchmark.task_type == "code"

    def test_syntax_error_in_code_is_false(self):
        q = _lcb_query([{"input": "1\n", "output": "2"}])
        assert self.bench.is_correct("def broken(:\n    pass", q) is False

    def test_all_cases_must_pass(self):
        q = _lcb_query([
            {"input": "2\n", "output": "4"},   # passes with n*2
            {"input": "3\n", "output": "99"},  # fails
        ])
        code = "n = int(input())\nprint(n * 2)"
        assert self.bench.is_correct(code, q) is False


# ================================================================
# HumanEval+ — is_correct (no dataset needed)
# ================================================================

def _hep_query(prompt: str, test_code: str, entry_point: str) -> Query:
    """Construct a HumanEval+-style Query with execution metadata."""
    return Query(
        id="HumanEval_test",
        text=f"Complete this function:\n```python\n{prompt}\n```",
        answer="    return a + b",
        metadata={
            "entry_point": entry_point,
            "test": test_code,
            "prompt": prompt,
        },
    )


_SIMPLE_PROMPT = "def add(a: int, b: int) -> int:\n    \"\"\"Add two numbers.\"\"\"\n"
_SIMPLE_TESTS = (
    "def check(candidate):\n"
    "    assert candidate(1, 2) == 3\n"
    "    assert candidate(-1, 5) == 4\n"
    "    assert candidate(0, 0) == 0\n"
)


class TestHumanEvalPlusIsCorrect:
    bench = HumanEvalPlusBenchmark.__new__(HumanEvalPlusBenchmark)

    def test_correct_function_body(self):
        q = _hep_query(_SIMPLE_PROMPT, _SIMPLE_TESTS, "add")
        assert self.bench.is_correct("    return a + b", q) is True

    def test_wrong_function_body(self):
        q = _hep_query(_SIMPLE_PROMPT, _SIMPLE_TESTS, "add")
        assert self.bench.is_correct("    return a - b", q) is False

    def test_none_response_is_false(self):
        q = _hep_query(_SIMPLE_PROMPT, _SIMPLE_TESTS, "add")
        assert self.bench.is_correct(None, q) is False

    def test_code_inside_fences_is_stripped(self):
        q = _hep_query(_SIMPLE_PROMPT, _SIMPLE_TESTS, "add")
        fenced = "```python\n    return a + b\n```"
        assert self.bench.is_correct(fenced, q) is True

    def test_task_type_is_code(self):
        assert HumanEvalPlusBenchmark.task_type == "code"

    def test_infinite_loop_times_out(self):
        q = _hep_query(
            "def spin() -> None:\n    \"\"\"Loop forever.\"\"\"\n",
            "def check(candidate):\n    candidate()\n",
            "spin",
        )
        # Should time out and return False, not hang the test suite
        assert self.bench.is_correct("    while True: pass", q) is False


# ================================================================
# Both benchmarks: task_type="code" flows through build_prompt/parse_answer
# ================================================================

class TestCodeTaskTypeIntegration:
    def test_build_prompt_returns_query_text_unmodified(self):
        q = Query(id="q", text="Solve this coding problem.\nReturn code only.", answer=None)
        # For code tasks, build_prompt must return query.text as-is —
        # the benchmark already embedded the full instructions.
        result = build_prompt(q, "code")
        assert result == q.text

    def test_parse_answer_returns_code_verbatim(self):
        code = "n = int(input())\nprint(n * 2)"
        assert parse_answer(code, "code") == code

    def test_parse_answer_none_returns_none(self):
        assert parse_answer(None, "code") is None

    def test_mcq_and_open_paths_unchanged(self):
        # Regression: existing task types must not be affected
        assert parse_answer("Answer: B", "mcq") == "B"
        assert parse_answer("Answer: 42", "open") == "42"
