"""
ARC-Challenge — AI2 Reasoning Challenge (hard subset)
=====================================================
Grade-school science MCQ. Hard questions that require reasoning.
Loaded from: allenai/ai2_arc, ARC-Challenge, test split.

Reference in SLR: S43, S29 — used for abstract reasoning evaluation.
"""
from __future__ import annotations

from benchmarks.base import BaseBenchmark
from core.types import Query


class ARCBenchmark(BaseBenchmark):
    name = "arc"
    task_type = "mcq"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test", trust_remote_code=True)
        queries: list[Query] = []
        for i, row in enumerate(ds):
            choices = row["choices"]
            choice_texts = choices["text"]
            choice_labels = choices["label"]
            answer_key = row["answerKey"]

            # Normalize label to A/B/C/D
            if answer_key in "ABCD":
                label = answer_key
            elif answer_key.isdigit():
                label = chr(64 + int(answer_key))
            else:
                label = answer_key

            # Re-order choices to always be A/B/C/D
            ordered_texts: list[str] = [""] * len(choice_texts)
            for text, lbl in zip(choice_texts, choice_labels):
                idx = ord(lbl[0]) - 65 if lbl[0] in "ABCD" else (int(lbl) - 1)
                if 0 <= idx < len(ordered_texts):
                    ordered_texts[idx] = text

            queries.append(
                Query(
                    id=f"arc_{i}",
                    text=row["question"],
                    choices=[t for t in ordered_texts if t],
                    answer=label,
                )
            )
        return queries
