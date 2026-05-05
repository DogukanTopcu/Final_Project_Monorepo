"""
TruthfulQA — Hallucination Resistance (MC1 subset)
====================================================
Tests whether models repeat common misconceptions.
MC1: single correct answer from 4 options.
Loaded from: truthful_qa, multiple_choice split.

Reference in SLR: S33 — uncertainty estimation and hallucination.
"""
from __future__ import annotations

from benchmarks.base import BaseBenchmark
from core.types import Query


class TruthfulQABenchmark(BaseBenchmark):
    name = "truthfulqa"
    task_type = "mcq"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("truthful_qa", "multiple_choice", split="validation", trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            mc1 = row["mc1_targets"]
            choices = mc1["choices"]
            labels = mc1["labels"]  # 1 = correct

            correct_idx = next((j for j, l in enumerate(labels) if l == 1), 0)
            # Rotate so correct is always option A (simplifies evaluation)
            rotated = [choices[correct_idx]] + [c for j, c in enumerate(choices) if j != correct_idx]
            rotated = rotated[:4]  # max 4 choices

            queries.append(
                Query(
                    id=f"truthfulqa_{i}",
                    text=row["question"],
                    choices=rotated,
                    answer="A",  # always A after rotation
                )
            )
        return queries
