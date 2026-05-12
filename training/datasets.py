from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with open(path) as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            records.append(record)
    return records


def write_jsonl(records: list[dict[str, Any]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def messages_to_text(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "")).strip()
        content = str(message.get("content", "")).strip()
        if not role or not content:
            continue
        parts.append(f"<|{role}|>\n{content}")
    return "\n".join(parts).strip()


def format_prompt_response(
    prompt: str,
    response: str,
    system_prompt: str | None = None,
) -> str:
    sections: list[str] = []
    if system_prompt:
        sections.append(f"<|system|>\n{system_prompt.strip()}")
    sections.append(f"<|user|>\n{prompt.strip()}")
    sections.append(f"<|assistant|>\n{response.strip()}")
    return "\n".join(sections).strip()


def normalize_sft_record(
    record: dict[str, Any],
    *,
    text_field: str = "text",
    prompt_field: str = "prompt",
    response_field: str = "response",
    system_prompt: str | None = None,
) -> dict[str, Any]:
    normalized = dict(record)

    if text_field in record and str(record[text_field]).strip():
        normalized[text_field] = str(record[text_field]).strip()
        return normalized

    if "messages" in record:
        messages = record["messages"]
        if not isinstance(messages, list):
            raise ValueError("messages must be a list")
        normalized[text_field] = messages_to_text(messages)
        return normalized

    if prompt_field not in record or response_field not in record:
        raise ValueError(
            f"Record must contain either '{text_field}', 'messages', or "
            f"'{prompt_field}' + '{response_field}'"
        )

    normalized[text_field] = format_prompt_response(
        str(record[prompt_field]),
        str(record[response_field]),
        system_prompt=system_prompt,
    )
    return normalized


def split_records(
    records: list[dict[str, Any]],
    *,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[dict[str, Any]]]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    if not 0 <= validation_ratio < 1:
        raise ValueError("validation_ratio must be between 0 and 1")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("train_ratio + validation_ratio must be less than 1")

    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)

    n_total = len(shuffled)
    n_train = int(n_total * train_ratio)
    n_validation = int(n_total * validation_ratio)

    train = shuffled[:n_train]
    validation = shuffled[n_train : n_train + n_validation]
    test = shuffled[n_train + n_validation :]
    return {"train": train, "validation": validation, "test": test}


def prepare_sft_dataset(
    input_path: str | Path,
    output_dir: str | Path,
    *,
    text_field: str = "text",
    prompt_field: str = "prompt",
    response_field: str = "response",
    system_prompt: str | None = None,
    train_ratio: float = 0.8,
    validation_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, Any]:
    records = read_jsonl(input_path)
    normalized = [
        normalize_sft_record(
            record,
            text_field=text_field,
            prompt_field=prompt_field,
            response_field=response_field,
            system_prompt=system_prompt,
        )
        for record in records
    ]
    splits = split_records(
        normalized,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        seed=seed,
    )

    output = Path(output_dir)
    paths = {
        "train": output / "train.jsonl",
        "validation": output / "validation.jsonl",
        "test": output / "test.jsonl",
    }
    for split_name, split_records_ in splits.items():
        write_jsonl(split_records_, paths[split_name])

    return {
        "input_path": str(input_path),
        "output_dir": str(output),
        "counts": {name: len(value) for name, value in splits.items()},
        "paths": {name: str(path) for name, path in paths.items()},
    }


def validate_dataset(path: str | Path, text_field: str = "text") -> dict[str, Any]:
    records = read_jsonl(path)
    missing = [i for i, record in enumerate(records) if not str(record.get(text_field, "")).strip()]
    return {"path": str(path), "n_records": len(records), "missing_text_rows": missing}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare SFT JSONL datasets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-sft")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--text-field", default="text")
    prepare.add_argument("--prompt-field", default="prompt")
    prepare.add_argument("--response-field", default="response")
    prepare.add_argument("--system-prompt")
    prepare.add_argument("--train-ratio", type=float, default=0.8)
    prepare.add_argument("--validation-ratio", type=float, default=0.1)
    prepare.add_argument("--seed", type=int, default=42)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--input", required=True)
    validate.add_argument("--text-field", default="text")

    args = parser.parse_args()
    if args.command == "prepare-sft":
        result = prepare_sft_dataset(
            args.input,
            args.output_dir,
            text_field=args.text_field,
            prompt_field=args.prompt_field,
            response_field=args.response_field,
            system_prompt=args.system_prompt,
            train_ratio=args.train_ratio,
            validation_ratio=args.validation_ratio,
            seed=args.seed,
        )
    else:
        result = validate_dataset(args.input, text_field=args.text_field)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

