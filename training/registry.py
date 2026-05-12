from __future__ import annotations

import argparse
import dataclasses
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class AdapterRecord:
    name: str
    base_model: str
    adapter_path: str
    domain: str
    task: str = "sft"
    source_dataset: str = ""
    training_config: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metrics: dict[str, float] = field(default_factory=dict)
    notes: str = ""


def load_registry(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path)
    if not registry_path.exists():
        return {"adapters": {}}
    with open(registry_path) as f:
        data = json.load(f)
    if "adapters" not in data or not isinstance(data["adapters"], dict):
        raise ValueError(f"Invalid adapter registry format: {registry_path}")
    return data


def save_registry(registry: dict[str, Any], path: str | Path) -> None:
    registry_path = Path(path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")


def register_adapter(path: str | Path, record: AdapterRecord) -> dict[str, Any]:
    registry = load_registry(path)
    registry["adapters"][record.name] = dataclasses.asdict(record)
    save_registry(registry, path)
    return registry


def get_adapter(path: str | Path, name: str) -> dict[str, Any]:
    registry = load_registry(path)
    try:
        return registry["adapters"][name]
    except KeyError as exc:
        raise KeyError(f"Adapter not found in registry: {name}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage fine-tuned adapter registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--registry", default="training/adapters/registry.json")

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--registry", default="training/adapters/registry.json")
    register_parser.add_argument("--name", required=True)
    register_parser.add_argument("--base-model", required=True)
    register_parser.add_argument("--adapter-path", required=True)
    register_parser.add_argument("--domain", required=True)
    register_parser.add_argument("--task", default="sft")
    register_parser.add_argument("--source-dataset", default="")
    register_parser.add_argument("--training-config", default="")
    register_parser.add_argument("--notes", default="")

    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(load_registry(args.registry), indent=2, ensure_ascii=False))
        return 0

    record = AdapterRecord(
        name=args.name,
        base_model=args.base_model,
        adapter_path=args.adapter_path,
        domain=args.domain,
        task=args.task,
        source_dataset=args.source_dataset,
        training_config=args.training_config,
        notes=args.notes,
    )
    registry = register_adapter(args.registry, record)
    print(json.dumps(registry["adapters"][args.name], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

