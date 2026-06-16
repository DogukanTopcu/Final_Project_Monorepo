"""Remove older result experiments while keeping only the newest N per group.

Grouping is done by ``(architecture, benchmark)``. Retention policy:

  * ``multi_agent``: keep latest 2
  * ``blackboard``: keep latest 2
  * ``entropy_blackboard``: keep latest 2
  * every other architecture: keep latest 1

By default this script performs a dry run and prints the experiments it would
remove. With ``--apply`` it removes matching experiments from the active
``results/`` directory.

Safety behavior:
  * default action is to move matching files into an archive directory under
    ``results/_removed_old_experiments/``
  * pass ``--delete`` together with ``--apply`` for permanent deletion
"""
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results"
DEFAULT_ARCHIVE_DIR = RESULTS_DIR / "_removed_old_experiments"
KEEP_TWO_ARCHITECTURES = {"multi_agent", "blackboard", "entropy_blackboard"}


@dataclass
class ExperimentRecord:
    json_path: Path
    md_path: Path
    experiment_id: str
    architecture: str
    benchmark: str
    created_at: str | None
    completed_at: str | None
    sort_timestamp: datetime


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _load_record(path: Path) -> ExperimentRecord | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  !! skipped {path.name}: failed to parse json ({type(exc).__name__}: {exc})")
        return None

    config = payload.get("config") or {}
    created_at = payload.get("created_at")
    completed_at = payload.get("completed_at")
    sort_timestamp = (
        _parse_timestamp(completed_at)
        or _parse_timestamp(created_at)
        or datetime.fromtimestamp(path.stat().st_mtime)
    )

    return ExperimentRecord(
        json_path=path,
        md_path=path.with_suffix(".md"),
        experiment_id=str(payload.get("experiment_id") or path.stem),
        architecture=str(config.get("architecture", "unknown")),
        benchmark=str(config.get("benchmark", "unknown")),
        created_at=created_at if isinstance(created_at, str) else None,
        completed_at=completed_at if isinstance(completed_at, str) else None,
        sort_timestamp=sort_timestamp,
    )


def _move_file(src: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        raise FileExistsError(f"archive target already exists: {dst}")
    shutil.move(str(src), str(dst))


def _remove_record(record: ExperimentRecord, archive_dir: Path | None, delete: bool) -> None:
    for file_path in (record.json_path, record.md_path):
        if not file_path.exists():
            continue
        if delete:
            file_path.unlink()
        else:
            assert archive_dir is not None
            _move_file(file_path, archive_dir)


def _retention_for_architecture(architecture: str) -> int:
    return 2 if architecture in KEEP_TWO_ARCHITECTURES else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help=f"directory containing exp_*.json files (default: {RESULTS_DIR})",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help=(
            "where to move removed files when using --apply without --delete "
            f"(default: {DEFAULT_ARCHIVE_DIR})"
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="perform the removal (default: dry run)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="permanently delete matching files instead of archiving them",
    )
    args = parser.parse_args()

    results_dir = args.results_dir.resolve()
    archive_dir = args.archive_dir.resolve()
    if args.delete and not args.apply:
        raise SystemExit("--delete requires --apply")

    grouped: dict[tuple[str, str], list[ExperimentRecord]] = {}
    for path in sorted(results_dir.glob("exp_*.json")):
        record = _load_record(path)
        if record is None:
            continue
        key = (record.architecture, record.benchmark)
        grouped.setdefault(key, []).append(record)

    removals: list[tuple[ExperimentRecord, int]] = []
    for (architecture, _benchmark), records in grouped.items():
        keep_count = _retention_for_architecture(architecture)
        ranked = sorted(
            records,
            key=lambda record: (record.sort_timestamp, record.experiment_id),
            reverse=True,
        )
        for record in ranked[keep_count:]:
            removals.append((record, keep_count))

    removals.sort(
        key=lambda item: (item[0].architecture, item[0].benchmark, item[0].sort_timestamp, item[0].experiment_id)
    )

    mode = "APPLY" if args.apply else "DRY RUN"
    action = "delete" if args.delete else f"archive to {archive_dir}"
    print(f"\n=== Remove old experiments by architecture — {mode} ===")
    print("Policy: multi_agent/blackboard/entropy_blackboard keep latest 2 per benchmark; others keep latest 1")
    print(f"Action: {action if args.apply else 'none (preview only)'}\n")

    if not removals:
        print("No matching experiments found.")
        return

    for record, keep_count in removals:
        timestamp = (record.completed_at or record.created_at or record.sort_timestamp.isoformat())
        print(
            f"{record.experiment_id:<16}"
            f"  {record.architecture:<18}"
            f"  {record.benchmark:<16}"
            f"  keep={keep_count}"
            f"  ts={timestamp}"
        )

    print(f"\nMatched {len(removals)} experiment(s).")

    if not args.apply:
        print("Re-run with --apply to remove them.")
        return

    removed = 0
    for record, _keep_count in removals:
        _remove_record(record, archive_dir=archive_dir, delete=args.delete)
        removed += 1

    verb = "deleted" if args.delete else "archived"
    print(f"Successfully {verb} {removed} experiment(s).")


if __name__ == "__main__":
    main()
