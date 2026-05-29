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
from typing import Any

from benchmarks._code_execution import run_io_tests, strip_code_fences
from benchmarks.base import BaseBenchmark
from core.types import Query

_DEFAULT_VERSION = "release_v5"
_DATASET_REPO = "livecodebench/code_generation_lite"

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


def _build_allowed_files() -> dict[str, list[str]]:
    allowed = {
        "release_v1": ["test.jsonl"],
        "release_v2": ["test.jsonl", "test2.jsonl"],
        "release_v3": ["test.jsonl", "test2.jsonl", "test3.jsonl"],
        "release_v4": ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl"],
        "release_v5": ["test.jsonl", "test2.jsonl", "test3.jsonl", "test4.jsonl", "test5.jsonl"],
        "release_v6": [
            "test.jsonl",
            "test2.jsonl",
            "test3.jsonl",
            "test4.jsonl",
            "test5.jsonl",
            "test6.jsonl",
        ],
    }
    allowed["release_latest"] = list(allowed["release_v6"])

    versions = [f"v{i}" for i in range(1, 7)]
    for idx, version in enumerate(versions, start=1):
        allowed[version] = [f"test{idx}.jsonl" if idx > 1 else "test.jsonl"]
    for start in range(1, len(versions) + 1):
        for end in range(start + 1, len(versions) + 1):
            allowed[f"v{start}_v{end}"] = [
                f"test{idx}.jsonl" if idx > 1 else "test.jsonl"
                for idx in range(start, end + 1)
            ]
    return allowed


_ALLOWED_FILES = _build_allowed_files()


def _files_for_version(version: str) -> list[str]:
    files = _ALLOWED_FILES.get(version)
    if files is None:
        supported = ", ".join(sorted(_ALLOWED_FILES))
        raise ValueError(
            f"Unsupported LiveCodeBench version_tag: {version!r}. "
            f"Expected one of: {supported}"
        )
    return list(files)


def _load_rows(version: str) -> list[dict[str, Any]]:
    from datasets import load_dataset  # type: ignore
    from huggingface_hub import hf_hub_download  # type: ignore

    # `datasets` 4.x removed support for Hub-hosted dataset scripts.
    # LiveCodeBench still stores its split-selection logic in that script,
    # so we reproduce the file mapping here and load the raw JSONL files.
    local_files = [
        hf_hub_download(
            repo_id=_DATASET_REPO,
            repo_type="dataset",
            filename=filename,
        )
        for filename in _files_for_version(version)
    ]
    dataset = load_dataset("json", data_files={"test": local_files}, split="test")
    return [dict(row) for row in dataset]


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
        queries: list[Query] = []
        for row in _load_rows(self.version):
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
