"""
MMLU — Massive Multitask Language Understanding
================================================
57 academic subjects, 4-choice MCQ.
Loaded from Hugging Face datasets: cais/mmlu  (all subjects, test split).

Reference in SLR: used as primary accuracy metric across multiple studies.
Default shot: 0-shot so SLM capability is unmasked.
"""
from __future__ import annotations

from benchmarks.base import BaseBenchmark
from core.types import Query

_SUBJECT = "all"


class MMLUBenchmark(BaseBenchmark):
    name = "mmlu"
    task_type = "mcq"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("cais/mmlu", _SUBJECT, split="test", trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            label = chr(65 + int(row["answer"]))  # 0→A, 1→B, ...
            queries.append(
                Query(
                    id=f"mmlu_{i}",
                    text=row["question"],
                    choices=row["choices"],
                    answer=label,
                    metadata={"subject": row.get("subject", "")},
                )
            )
        return queries
