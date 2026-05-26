"""Prompt templates for MCQ and open-ended benchmarks."""
from __future__ import annotations

import re

from core.types import Query


def _choice_labels(query: Query) -> list[str]:
    count = len(query.choices or [])
    return [chr(65 + i) for i in range(count)]


def mcq_prompt(query: Query, few_shot: int = 0) -> str:
    """Multiple-choice question prompt used for MMLU, ARC, HellaSwag, TruthfulQA."""
    lines = [query.text, ""]
    labels = _choice_labels(query)
    if query.choices:
        for i, choice in enumerate(query.choices):
            label = labels[i]
            lines.append(f"{label}. {choice}")
    label_hint = ", ".join(labels) if labels else "the matching option letter"
    lines += [
        "",
        f"Choose the single best answer: {label_hint}.",
        "End your response with a final line in the format: Answer: <LETTER>",
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
    normalized = text.strip().upper()
    if len(normalized) == 1 and normalized.isalpha():
        return normalized

    explicit_patterns = [
        r"\bANSWER\s*:\s*([A-Z])\b",
        r"\bFINAL\s+ANSWER\s*:\s*([A-Z])\b",
        r"\bTHE\s+ANSWER\s+IS\s+([A-Z])\b",
        r"\bI\s+CHOOSE\s+([A-Z])\b",
        r"\bI\s+PICK\s+([A-Z])\b",
        r"\bOPTION\b[ \t]*[:\-\(]?[ \t]*([A-Z])\b",
    ]
    for pattern in explicit_patterns:
        matches = list(re.finditer(pattern, normalized, re.MULTILINE))
        if matches:
            return matches[-1].group(1)

    fallback_patterns = [
        r"^\s*\(([A-Z])\)\s*$",
        r"^\s*([A-Z])[\.\)]?\s*$",
    ]
    non_empty_lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    for line in reversed(non_empty_lines):
        for pattern in fallback_patterns:
            match = re.fullmatch(pattern, line)
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
