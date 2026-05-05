"""
GSM8K — Grade School Math
==========================
Open-ended arithmetic word problems requiring multi-step reasoning.
Task type: "open" (not MCQ).
Loaded from: openai/gsm8k, main split, test.

Reference in SLR: S4 — CoT reasoning increases per-query energy use.
This benchmark directly tests whether SLMs can handle Chain-of-Thought.
"""
from __future__ import annotations

import re

from benchmarks.base import BaseBenchmark
from core.types import Query


def _extract_answer(solution: str) -> str | None:
    m = re.search(r"####\s*(-?\d[\d,\.]*)", solution)
    if m:
        return m.group(1).replace(",", "")
    return None


class GSM8KBenchmark(BaseBenchmark):
    name = "gsm8k"
    task_type = "open"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("openai/gsm8k", "main", split="test", trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            answer = _extract_answer(row["answer"])
            queries.append(
                Query(
                    id=f"gsm8k_{i}",
                    text=row["question"],
                    choices=None,
                    answer=answer,
                )
            )
        return queries

    def is_correct(self, response_text: str | None, query: Query) -> bool:
        if response_text is None or query.answer is None:
            return False
        try:
            pred = float(response_text.replace(",", ""))
            gold = float(query.answer.replace(",", ""))
            return abs(pred - gold) < 1e-3
        except ValueError:
            return response_text.strip() == query.answer.strip()
