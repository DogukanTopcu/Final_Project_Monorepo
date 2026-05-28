"""
LiveCodeBench — Contamination-free competitive programming benchmark
====================================================================
Collects problems from LeetCode, AtCoder, and Codeforces published
after model training cutoffs, ensuring temporal contamination control.
Native easy / medium / hard difficulty labels feed our subject-accuracy
disaggregation without any additional annotation.

Metric:  pass@1 on public test cases at temperature=0
Dataset: livecodebench/code_generation_lite on Hugging Face
Version: release_v5 (880 problems, May 2023 – Jan 2025) by default
Scoring: run_io_tests — stdin/stdout execution against all public cases

Why this over HumanEval+:
  HumanEval+ is still likely in training data for models trained through
  late 2023. LiveCodeBench problems are published after the training cutoff
  of the models under evaluation, so results reflect genuine capability.

Reference:
  Jain et al. 2024 — "LiveCodeBench: Holistic and Contamination Free
  Evaluation of Large Language Models for Code"
  https://arxiv.org/abs/2403.07974
"""
from __future__ import annotations

import json

from benchmarks._code_execution import run_io_tests, strip_code_fences
from benchmarks.base import BaseBenchmark
from core.types import Query


_DEFAULT_VERSION = "release_v5"

_PROMPT_TEMPLATE = """\
{problem}

Write a complete Python solution. Read input from standard input (stdin) and \
write output to standard output (stdout). Do not include any explanation."""

_PROMPT_WITH_STARTER = """\
{problem}

Reference starter code (adapt as needed — write a complete standalone solution):
```python
{starter}
```

Write a complete Python solution. Read input from standard input (stdin) and \
write output to standard output (stdout). Do not include any explanation."""


def _normalize_difficulty(raw: str | int | None) -> str:
    """Map platform-native difficulty labels to easy / medium / hard."""
    if raw is None:
        return "medium"
    s = str(raw).lower().strip()
    if s in ("easy", "0"):
        return "easy"
    if s in ("hard", "2", "3"):
        return "hard"
    return "medium"  # catches "medium", "1", and anything unexpected


def _parse_test_cases(raw: str | None) -> list[dict]:
    """Parse public_test_cases JSON string into list of {input, output} dicts."""
    if not raw:
        return []
    try:
        cases = json.loads(raw)
        if not isinstance(cases, list):
            return []
        result = []
        for tc in cases:
            if not isinstance(tc, dict):
                continue
            # Only handle stdin/stdout test types — skip expression-based checks
            if tc.get("testtype", "stdin") not in ("stdin", ""):
                continue
            result.append({
                "input": str(tc.get("input", "")),
                "output": str(tc.get("output", "")).strip(),
            })
        return result
    except (json.JSONDecodeError, TypeError):
        return []


class LiveCodeBenchBenchmark(BaseBenchmark):
    name = "livecodebench"
    task_type = "code"

    def __init__(
        self,
        n_samples: int = 100,
        seed: int = 42,
        version: str = _DEFAULT_VERSION,
    ) -> None:
        super().__init__(n_samples=n_samples, seed=seed)
        self.version = version

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset(
            "livecodebench/code_generation_lite",
            version_tag=self.version,
            split="test",
        )
        queries: list[Query] = []
        for row in ds:
            test_cases = _parse_test_cases(row.get("public_test_cases"))
            if not test_cases:
                # Skip problems with no evaluable public test cases
                continue

            difficulty = _normalize_difficulty(row.get("difficulty"))
            starter = (row.get("starter_code") or "").strip()
            problem = (row.get("question_content") or "").strip()

            prompt = (
                _PROMPT_WITH_STARTER.format(problem=problem, starter=starter)
                if starter
                else _PROMPT_TEMPLATE.format(problem=problem)
            )

            queries.append(
                Query(
                    id=f"lcb_{row['question_id']}",
                    text=prompt,
                    answer=None,
                    metadata={
                        "difficulty": difficulty,
                        "platform": row.get("platform", ""),
                        "title": row.get("question_title", ""),
                        "contest_date": str(row.get("contest_date", "")),
                        "test_cases": test_cases,
                    },
                )
            )
        return queries

    def is_correct(self, response_text: str | None, query: Query) -> bool:
        if response_text is None:
            return False
        test_cases: list[dict] = query.metadata.get("test_cases", [])
        if not test_cases:
            return False
        return run_io_tests(
            code=strip_code_fences(response_text),
            test_cases=test_cases,
        )
