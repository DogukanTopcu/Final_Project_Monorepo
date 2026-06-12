"""Prompt templates for MCQ and open-ended benchmarks."""
from __future__ import annotations

import re

from core.types import Query


def _trim_blank_lines(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def normalize_code_answer(text: str) -> str | None:
    """Normalize code-task outputs while preserving code indentation.

    Models sometimes wrap otherwise-correct code inside Markdown fences or add
    extra blank lines around the snippet. For code-generation benchmarks we
    treat those wrappers as presentation noise and keep only the code itself.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines()

    fence_start: int | None = None
    fence_end: int | None = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("```"):
            if fence_start is None:
                fence_start = idx
            else:
                fence_end = idx
                break

    if fence_start is not None and fence_end is not None:
        candidate_lines = lines[fence_start + 1:fence_end]
    else:
        candidate_lines = [
            line for line in lines if not line.strip().startswith("```")
        ]

    candidate_lines = _trim_blank_lines(candidate_lines)
    if not candidate_lines:
        return None

    normalized_code = "\n".join(candidate_lines)
    return normalized_code if normalized_code.strip() else None


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
        "Solve the problem step-by-step. "
        "End your response with a final line in the exact format:\n"
        "Answer: <number>"
    )


def parse_mcq_answer(text: str) -> str | None:
    """Extract single-letter MCQ answer from model output."""
    normalized = text.strip().upper()
    normalized = re.sub(r"[*_`]+", "", normalized)
    if len(normalized) == 1 and normalized.isalpha():
        return normalized

    explicit_patterns = [
        r"\bANSWER\s*:\s*([A-Z])\b",
        r"\bFINAL\s+ANSWER\s*:\s*([A-Z])\b",
        r"\bCORRECT\s+ANSWER\s+IS\s+([A-Z])\b",
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


def build_prompt(query: Query, task_type: str) -> str:
    """Single entry point for prompt construction across all task types."""
    if task_type == "mcq":
        return mcq_prompt(query)
    if task_type == "code":
        return query.text  # query text already contains full coding instructions
    return open_prompt(query)


def parse_answer(text: str | None, task_type: str) -> str | None:
    """Single entry point for answer extraction across all task types."""
    if text is None:
        return None
    if task_type == "mcq":
        return parse_mcq_answer(text)
    if task_type == "code":
        return normalize_code_answer(text)
    return parse_open_answer(text)


def parse_open_answer(text: str) -> str | None:
    """Extract numeric answer from open-ended output (GSM8K)."""
    stripped = text.strip()
    if not stripped:
        return None

    # Leading [\s*_#>]* tolerates markdown emphasis/heading/quote markers and the
    # trailing \**  the closing bold, so a model that writes "**Answer: 80**"
    # (e.g. gpt-oss-120b) is parsed the same as a plain "Answer: 80". The lines
    # stay anchored to start/end so we never grab a stray number from reasoning.
    patterns = [
        r"(?im)^[\s*_#>]*Answer:\s*\**\s*(-?\d[\d,\.]*)\s*\**\s*$",
        r"(?im)^[\s*_#>]*Final Answer:\s*\**\s*(-?\d[\d,\.]*)\s*\**\s*$",
        r"(?im)^[\s*_#>]*The answer is\s*\**\s*(-?\d[\d,\.]*)\s*\**\s*$",
        r"(?im)^[\s*_#>]*(-?\d[\d,\.]*)\s*\**\s*$",
    ]
    for pattern in patterns:
        match = re.search(pattern, stripped)
        if match:
            return match.group(1).replace(",", "")
    return None
