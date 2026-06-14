"""Detect and fix result files whose eats_score uses a deprecated formula.

A run is "current-formula" iff its stored eats_score equals
``compute_eats(accuracy, normalized_cost, normalized_algorithmic_latency,
normalized_energy)`` for its stored normalized components. Anything else was
written by an older harness and is rewritten onto the current formula.

Safety rule for missing (None) normalized components:
  * monolithic runs ARE the baseline → every normalized component is 1.0 by
    definition, so a None is safely filled with 1.0.
  * non-monolithic runs normalize against a separate baseline; a None there
    means the data to recompute the ratio is not in the file. Those are NOT
    auto-filled — they're reported as "needs-baseline" and left untouched so we
    never fabricate a normalization.

Usage:
    python scripts/normalize_eats.py            # dry run: classify every file
    python scripts/normalize_eats.py --apply    # rewrite the fixable ones
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.types import ExperimentConfig, ExperimentResult
from evaluation.metrics import (
    compute_accuracy_deficit_penalty,
    compute_eats,
    compute_efficiency_penalty,
)
from evaluation.reporter import Reporter

RESULTS = Path(__file__).resolve().parent.parent / "results"
BACKUP = RESULTS / "_pre_rescore_backup"
TOL = 1e-6


def _f(v, default=None):
    return float(v) if isinstance(v, (int, float)) else default


def classify(path: Path) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = data.get("config") or {}
    m = data.get("metrics") or {}
    if "accuracy" not in m or "eats_score" not in m:
        return None

    arch = cfg.get("architecture")
    acc = _f(m.get("accuracy"), 0.0)
    stored = _f(m.get("eats_score"))
    nc = _f(m.get("normalized_cost"))
    nl = _f(m.get("normalized_algorithmic_latency"))
    ne = _f(m.get("normalized_energy"))

    missing = [name for name, v in (("cost", nc), ("latency", nl), ("energy", ne)) if v is None]
    is_baseline = arch == "monolithic"

    # Resolve the normalized components we'll score EATS with.
    if missing and not is_baseline:
        status = "needs-baseline"   # cannot safely recompute — leave it
        rnc = rnl = rne = None
        recomputed = None
    else:
        rnc = nc if nc is not None else 1.0
        rnl = nl if nl is not None else 1.0
        rne = ne if ne is not None else 1.0
        recomputed = compute_eats(
            accuracy=acc, normalized_cost=rnc,
            normalized_algorithmic_latency=rnl, normalized_energy=rne,
        )
        if stored is not None and abs(stored - recomputed) <= TOL:
            status = "current"      # already on the new formula
        else:
            status = "fixable"      # old formula → rewrite

    return {
        "path": path, "data": data, "metrics": m, "config": cfg,
        "experiment_id": data.get("experiment_id", path.stem),
        "arch": arch, "benchmark": cfg.get("benchmark"),
        "acc": acc, "stored": stored, "recomputed": recomputed,
        "rnc": rnc, "rnl": rnl, "rne": rne, "missing": missing, "status": status,
    }


def apply_fix(rec: dict) -> None:
    path, data, m = rec["path"], rec["data"], rec["metrics"]
    nc, nl, ne = rec["rnc"], rec["rnl"], rec["rne"]
    m["normalized_cost"] = nc
    m["normalized_algorithmic_latency"] = nl
    m["normalized_energy"] = ne
    m["normalized_efficiency_penalty"] = compute_efficiency_penalty(
        normalized_cost=nc,
        normalized_algorithmic_latency=nl,
        normalized_energy=ne,
    )
    m["accuracy_deficit_penalty"] = compute_accuracy_deficit_penalty(rec["acc"])
    m["eats_score"] = rec["recomputed"]

    BACKUP.mkdir(parents=True, exist_ok=True)
    for ext in (".json", ".md"):
        src = path.with_suffix(ext)
        if src.exists() and not (BACKUP / src.name).exists():
            shutil.copy2(src, BACKUP / src.name)

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    fields = ExperimentConfig.__dataclass_fields__
    result = ExperimentResult(
        experiment_id=rec["experiment_id"],
        config=ExperimentConfig(**{k: v for k, v in rec["config"].items() if k in fields}),
        samples=[],
    )
    report_for_md = {"created_at": data.get("completed_at") or data.get("created_at", "")}
    Reporter(RESULTS)._write_markdown(
        path.with_suffix(".md"), report_for_md, m, result, subject_accuracy={}
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="rewrite fixable files (default: dry run)")
    args = ap.parse_args()

    recs = []
    for f in sorted(RESULTS.glob("exp_*.json")):
        try:
            r = classify(f)
        except Exception as e:  # noqa: BLE001
            print(f"  !! {f.name}: {type(e).__name__}: {e}")
            continue
        if r:
            recs.append(r)

    by_status = {"fixable": [], "current": [], "needs-baseline": []}
    for r in recs:
        by_status[r["status"]].append(r)

    print(f"\n=== EATS formula audit — {'APPLIED' if args.apply else 'DRY RUN'} ===\n")
    if by_status["fixable"]:
        print("FIXABLE (old formula → current):")
        for r in by_status["fixable"]:
            print(f"  {r['experiment_id']:<16}{str(r['arch']):<14}{str(r['benchmark']):<10}"
                  f"eats {r['stored']:.4f} → {r['recomputed']:.4f}"
                  + (f"   [filled: {','.join(r['missing'])}]" if r['missing'] else ""))
            if args.apply:
                apply_fix(r)
    else:
        print("FIXABLE: none")

    if by_status["needs-baseline"]:
        print("\nNEEDS-BASELINE (non-monolithic w/ missing normalization — left untouched):")
        for r in by_status["needs-baseline"]:
            print(f"  {r['experiment_id']:<16}{str(r['arch']):<14}{str(r['benchmark']):<10}"
                  f"eats {r['stored']:.4f}   missing: {','.join(r['missing'])}")

    print(f"\n{len(recs)} files · {len(by_status['fixable'])} fixable · "
          f"{len(by_status['current'])} already current · {len(by_status['needs-baseline'])} needs-baseline")
    if by_status["fixable"] and not args.apply:
        print("\nRe-run with --apply to rewrite the fixable files (originals backed up).")


if __name__ == "__main__":
    main()
