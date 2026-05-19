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
        "You must answer with exactly one uppercase letter: A, B, C, or D.",
        "Do not include any explanation.",
    ]
    return "\n".join(lines)


def open_prompt(query: Query) -> str:
    """Open-ended prompt used for GSM8K."""
    return (
        f"{query.text}\n\n"
        "Solve carefully and return only the final numeric answer on the last line as:\n"
        "Answer: <number>\n"
        "Do not include chain-of-thought or explanation."
    )


def parse_mcq_answer(text: str) -> str | None:
    """Extract single-letter MCQ answer from model output."""
    import re
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
    import re
    m = re.search(r"Answer:\s*(-?\d[\d,\.]*)", text, re.IGNORECASE)
    if m:
        return m.group(1).replace(",", "")
    # Fallback: last number in text
    numbers = re.findall(r"-?\d[\d,\.]*", text)
    return numbers[-1].replace(",", "") if numbers else None
