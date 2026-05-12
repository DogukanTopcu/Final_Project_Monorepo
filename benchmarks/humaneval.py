"""Project HumanEval benchmark plan.

In this project, "HumanEval" means human preference evaluation through the
product UI, not the OpenAI HumanEval code-generation dataset.

Planned surfaces:
  1. LLM Arena: users evaluate answers produced for prepared prompts.
  2. Live chat: users ask their own question; multiple architectures answer;
     the user selects the better response, with ties allowed.

Planned record shape:
  - prompt_id, prompt_text, prompt_source, task_category
  - architecture_a, architecture_b, answer_a, answer_b
  - randomized_display_order, selected_winner, tie/skip flag
  - evaluator_id/session_id, timestamp, optional rationale/rating
  - latency/cost/token metadata for each architecture

The implementation below is a legacy OpenAI HumanEval prototype. It should not
be treated as the target benchmark until it is replaced by the UI-backed human
preference pipeline described above.
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
