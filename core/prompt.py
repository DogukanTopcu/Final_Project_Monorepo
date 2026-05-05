"""Prompt templates for MCQ and open-ended benchmarks."""
from __future__ import annotations

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
        "Answer with the letter only (A, B, C or D).",
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
    import re
    text = text.strip().upper()
    # Direct letter
    if text and text[0] in "ABCD":
        return text[0]
    # Pattern: "Answer: B" or "(B)"
    m = re.search(r"\b([ABCD])\b", text)
    return m.group(1) if m else None


def parse_open_answer(text: str) -> str | None:
    """Extract numeric answer from open-ended output (GSM8K)."""
    import re
    m = re.search(r"Answer:\s*(-?\d[\d,\.]*)", text, re.IGNORECASE)
    if m:
        return m.group(1).replace(",", "")
    # Fallback: last number in text
    numbers = re.findall(r"-?\d[\d,\.]*", text)
    return numbers[-1].replace(",", "") if numbers else None
