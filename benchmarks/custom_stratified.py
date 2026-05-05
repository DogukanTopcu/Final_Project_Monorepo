"""Custom stratified benchmark — Easy / Medium / Hard (300 / 400 / 300).

Draws from MMLU and GSM8K to build a 1,000-query set balanced across
difficulty tiers. Difficulty is assigned via a proxy heuristic:
  - Easy:   short MCQ questions, single-step reasoning
  - Medium: multi-step MCQ or moderate math
  - Hard:   complex multi-hop or 3+ step GSM8K problems

The split is deterministic (fixed random seed) so results are reproducible.
"""
from __future__ import annotations

import random
from enum import Enum

from datasets import load_dataset

from core.types import Query
from benchmarks.base import Benchmark


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


_SEED = 42
_EASY_N = 300
_MEDIUM_N = 400
_HARD_N = 300

# MMLU subjects mapped to difficulty tier
_EASY_SUBJECTS = {
    "high_school_us_history", "high_school_world_history",
    "elementary_mathematics", "nutrition",
}
_HARD_SUBJECTS = {
    "abstract_algebra", "college_mathematics", "college_physics",
    "electrical_engineering", "formal_logic", "high_school_mathematics",
    "professional_law", "jurisprudence",
}


def _mmlu_difficulty(subject: str, choices: list[str]) -> Difficulty:
    if subject in _EASY_SUBJECTS:
        return Difficulty.EASY
    if subject in _HARD_SUBJECTS:
        return Difficulty.HARD
    return Difficulty.MEDIUM


def _gsm8k_difficulty(answer: str) -> Difficulty:
    """Heuristic: number of calculation steps ≈ number of '=' signs in solution."""
    steps = answer.count("=")
    if steps <= 2:
        return Difficulty.EASY
    if steps <= 5:
        return Difficulty.MEDIUM
    return Difficulty.HARD


class CustomStratifiedBenchmark(Benchmark):
    name = "custom_stratified"

    def __init__(self, seed: int = _SEED) -> None:
        self.seed = seed
        self._queries: list[Query] = []

    def load(self) -> list[Query]:
        rng = random.Random(self.seed)
        buckets: dict[Difficulty, list[Query]] = {d: [] for d in Difficulty}

        # --- MMLU ---
        ds_mmlu = load_dataset("cais/mmlu", "all", split="test", trust_remote_code=True)
        choices_map = ["A", "B", "C", "D"]
        for i, row in enumerate(ds_mmlu):
            choices = row["choices"]
            subject = row.get("subject", "")
            diff = _mmlu_difficulty(subject, choices)
            answer_letter = choices_map[row["answer"]]
            q = Query(
                id=f"mmlu_{i}",
                text=row["question"],
                choices=choices,
                answer=answer_letter,
                metadata={"source": "mmlu", "subject": subject, "difficulty": diff.value},
            )
            buckets[diff].append(q)

        # --- GSM8K ---
        ds_gsm = load_dataset("openai/gsm8k", "main", split="test", trust_remote_code=True)
        for i, row in enumerate(ds_gsm):
            raw_answer = row["answer"]
            parts = raw_answer.split("####")
            numeric_answer = parts[-1].strip().replace(",", "") if len(parts) > 1 else ""
            diff = _gsm8k_difficulty(raw_answer)
            q = Query(
                id=f"gsm8k_{i}",
                text=row["question"],
                answer=numeric_answer,
                metadata={"source": "gsm8k", "difficulty": diff.value, "full_solution": raw_answer},
            )
            buckets[diff].append(q)

        # Shuffle and trim to target sizes
        for diff in Difficulty:
            rng.shuffle(buckets[diff])

        selected: list[Query] = (
            buckets[Difficulty.EASY][:_EASY_N]
            + buckets[Difficulty.MEDIUM][:_MEDIUM_N]
            + buckets[Difficulty.HARD][:_HARD_N]
        )
        rng.shuffle(selected)
        self._queries = selected
        return selected
