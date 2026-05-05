"""HumanEval benchmark — 164 Python code-generation problems.

Ground-truth evaluation requires executing the generated code against the
provided unit tests in a sandboxed subprocess. This module handles loading,
prompt construction, and correctness checking.

Safety: code is executed with a 10-second timeout inside a restricted
subprocess. Never run this outside a sandboxed environment (Docker with
--network none is recommended).
"""
from __future__ import annotations

import ast
import subprocess
import sys
import textwrap
import tempfile
import os
from pathlib import Path

from datasets import load_dataset

from core.types import Query
from benchmarks.base import Benchmark


_INSTRUCTION = (
    "Complete the following Python function. "
    "Return only the function body (no import statements, no extra explanation)."
)


class HumanEvalBenchmark(Benchmark):
    name = "humaneval"

    def __init__(self, split: str = "test", max_samples: int | None = None) -> None:
        self.split = split
        self.max_samples = max_samples
        self._queries: list[Query] = []

    def load(self) -> list[Query]:
        ds = load_dataset("openai/openai_humaneval", split=self.split, trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            if self.max_samples and i >= self.max_samples:
                break
            prompt = row["prompt"]
            text = f"{_INSTRUCTION}\n\n```python\n{prompt}\n```"
            queries.append(
                Query(
                    id=row["task_id"].replace("/", "_"),
                    text=text,
                    answer=row["canonical_solution"],
                    metadata={
                        "entry_point": row["entry_point"],
                        "test": row["test"],
                        "prompt": prompt,
                    },
                )
            )
        self._queries = queries
        return queries

    def check_correct(self, query: Query, predicted: str) -> bool:
        """Execute generated code against HumanEval unit tests."""
        prompt: str = query.metadata.get("prompt", "")
        entry_point: str = query.metadata.get("entry_point", "")
        test_code: str = query.metadata.get("test", "")

        # Strip markdown code fences if model wrapped the answer
        code = _strip_code_fences(predicted)

        full_program = textwrap.dedent(f"""
{prompt}
{code}

{test_code}

check({entry_point})
""")
        return _run_in_sandbox(full_program)


def _strip_code_fences(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or in_fence:
            out.append(line)
    return "\n".join(out)


def _run_in_sandbox(code: str, timeout: int = 10) -> bool:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            [sys.executable, fname],
            capture_output=True,
            timeout=timeout,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass
