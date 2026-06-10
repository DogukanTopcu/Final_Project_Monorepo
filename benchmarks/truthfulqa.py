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

        ds = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
        queries: list[Query] = []
        for i, row in enumerate(ds):
            mc1 = row["mc1_targets"]
            choices = mc1["choices"]
            labels = mc1["labels"]  # 1 = correct

            correct_idx = next((j for j, lbl in enumerate(labels) if lbl == 1), 0)
            # Keep original shuffled order — rotating to always place the
            # correct answer at A introduces position bias (models favour A).
            # The dataset was pre-shuffled at creation time, so correct_idx
            # is already uniformly distributed across positions.
            queries.append(
                Query(
                    id=f"truthfulqa_{i}",
                    text=row["question"],
                    choices=choices,
                    answer=chr(65 + correct_idx),
                )
            )
        return queries
