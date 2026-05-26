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


def _normalize_choice_label(value: str) -> str:
    token = value.strip().upper()
    if len(token) == 1 and token.isalpha():
        return token
    if token.isdigit():
        return chr(64 + int(token))
    raise ValueError(f"Unsupported ARC choice label: {value!r}")


def _choice_index(value: str) -> int:
    normalized = _normalize_choice_label(value)
    return ord(normalized) - 65


class ARCBenchmark(BaseBenchmark):
    name = "arc"
    task_type = "mcq"

    def _load_all(self) -> list[Query]:
        from datasets import load_dataset  # type: ignore

        ds = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
        queries: list[Query] = []
        for i, row in enumerate(ds):
            choices = row["choices"]
            choice_texts = choices["text"]
            choice_labels = choices["label"]
            answer_key = row["answerKey"]

            label = _normalize_choice_label(answer_key)

            # Re-order choices to canonical A/B/C/... label order.
            ordered_texts: list[str] = [""] * len(choice_texts)
            for text, lbl in zip(choice_texts, choice_labels):
                idx = _choice_index(str(lbl))
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
