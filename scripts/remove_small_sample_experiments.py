"""Remove result experiments whose sample count is below a minimum threshold.

By default this script performs a dry run and prints the experiments it would
remove. With ``--apply`` it removes matching experiments from the active
``results/`` directory.

Safety behavior:
  * default action is to move matching files into an archive directory under
    ``results/_removed_small_sample_experiments/``
  * pass ``--delete`` together with ``--apply`` for permanent deletion

The script inspects each ``results/exp_*.json`` file and resolves the sample
count from, in order:
  1. ``metrics.n_total``
  2. ``len(samples)``
  3. ``config.n_samples``
"""
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results"
DEFAULT_ARCHIVE_DIR = RESULTS_DIR / "_removed_small_sample_experiments"


@dataclass
class ExperimentRecord:
    json_path: Path
    md_path: Path
    experiment_id: str
    architecture: str
    benchmark: str
    sample_count: int


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def _resolve_sample_count(payload: dict) -> int:
    metrics = payload.get("metrics") or {}
    samples = payload.get("samples") or []
    config = payload.get("config") or {}

    n_total = _as_int(metrics.get("n_total"))
    if n_total is not None:
        return n_total
    if isinstance(samples, list):
        return len(samples)
    n_samples = _as_int(config.get("n_samples"))
    if n_samples is not None:
        return n_samples
    return 0


def _load_record(path: Path) -> ExperimentRecord | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  !! skipped {path.name}: failed to parse json ({type(exc).__name__}: {exc})")
        return None

    config = payload.get("config") or {}
    experiment_id = str(payload.get("experiment_id") or path.stem)
    return ExperimentRecord(
        json_path=path,
        md_path=path.with_suffix(".md"),
        experiment_id=experiment_id,
        architecture=str(config.get("architecture", "unknown")),
        benchmark=str(config.get("benchmark", "unknown")),
        sample_count=_resolve_sample_count(payload),
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-samples",
        type=int,
        default=100,
        help="keep experiments with at least this many samples (default: 100)",
    )
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
    if args.min_samples < 0:
        raise SystemExit("--min-samples must be >= 0")
    if args.delete and not args.apply:
        raise SystemExit("--delete requires --apply")

    records: list[ExperimentRecord] = []
    for path in sorted(results_dir.glob("exp_*.json")):
        record = _load_record(path)
        if record is None:
            continue
        if record.sample_count < args.min_samples:
            records.append(record)

    mode = "APPLY" if args.apply else "DRY RUN"
    action = "delete" if args.delete else f"archive to {archive_dir}"
    print(f"\n=== Remove small-sample experiments — {mode} ===")
    print(f"Threshold: keep >= {args.min_samples} samples")
    print(f"Action: {action if args.apply else 'none (preview only)'}\n")

    if not records:
        print("No matching experiments found.")
        return

    for record in records:
        print(
            f"{record.experiment_id:<16}"
            f"  {record.architecture:<18}"
            f"  {record.benchmark:<16}"
            f"  samples={record.sample_count}"
        )

    print(f"\nMatched {len(records)} experiment(s).")

    if not args.apply:
        print("Re-run with --apply to remove them.")
        return

    removed = 0
    for record in records:
        _remove_record(record, archive_dir=archive_dir, delete=args.delete)
        removed += 1

    verb = "deleted" if args.delete else "archived"
    print(f"Successfully {verb} {removed} experiment(s).")


if __name__ == "__main__":
    main()
