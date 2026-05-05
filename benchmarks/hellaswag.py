"""
HellaSwag — Commonsense NLI
============================
Sentence completion task, 4-choice MCQ.
Tests commonsense reasoning — SLMs typically struggle here.
Loaded from: Rowan/hellaswag, validation split.
"""
from __future__ import annotations

import re

from benchmarks.base import BaseBenchmark
from core.types import Query


def _clean(text: str) -> str:
    return re.sub(r"\[.*?\]", "", text).strip()


class HellaSwagBenchmark(BaseBenchmark):
    name = "hellaswag"
    task_type = "mcq"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("Rowan/hellaswag", split="validation", trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            ctx = _clean(row["ctx"])
            endings = [_clean(e) for e in row["endings"]]
            label = chr(65 + int(row["label"]))
            queries.append(
                Query(
                    id=f"hellaswag_{i}",
                    text=f"Complete the following:\n{ctx}",
                    choices=endings,
                    answer=label,
                    metadata={"activity_label": row.get("activity_label", "")},
                )
            )
        return queries
