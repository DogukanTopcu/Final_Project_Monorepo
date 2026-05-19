"""Prompt templates for MCQ and open-ended benchmarks."""
from __future__ import annotations

import re

from core.types import Query


def mcq_prompt(query: Query, few_shot: int = 0) -> str:
    """Multiple-choice question prompt used for MMLU, ARC, HellaSwag, TruthfulQA."""
    lines = [query.text, ""]
    if query.choices:
        for i, choice in enumerate(query.choices):
            label = chr(65 + i)  # A, B, C, D
            lines.append(f"{label}. {choice}")
    lines += [
        "",
        "You must answer with exactly one uppercase letter: A, B, C, or D.",
        "Do not include any explanation.",
    ]
    return "\n".join(lines)


def open_prompt(query: Query) -> str:
    """Open-ended prompt used for GSM8K."""
    return (
        f"{query.text}\n\n"
        "Think step by step, then give the final numeric answer on the last line as:\n"
        "Answer: <number>"
    )


def parse_mcq_answer(text: str) -> str | None:
    """Extract single-letter MCQ answer from model output."""
    normalized = text.strip().upper()
    if normalized in {"A", "B", "C", "D"}:
        return normalized

    patterns = [
        r"^\s*([ABCD])[\.\)]?\s*$",
        r"\bANSWER\s*:\s*([ABCD])\b",
        r"\bFINAL\s+ANSWER\s*:\s*([ABCD])\b",
        r"\bOPTION\s*([ABCD])\b",
        r"^\s*\(([ABCD])\)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, re.MULTILINE)
        if match:
            return match.group(1)
    return None


def parse_open_answer(text: str) -> str | None:
    """Extract numeric answer from open-ended output (GSM8K)."""
    stripped = text.strip()
    if not stripped:
        return None

    patterns = [
        r"(?im)^\s*Answer:\s*(-?\d[\d,\.]*)\s*$",
        r"(?im)^\s*Final Answer:\s*(-?\d[\d,\.]*)\s*$",
        r"(?im)^\s*The answer is\s*(-?\d[\d,\.]*)\s*$",
        r"(?im)^\s*(-?\d[\d,\.]*)\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, stripped)
        if match:
            return match.group(1).replace(",", "")
    return None
