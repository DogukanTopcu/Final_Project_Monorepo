"""Re-score GSM8K result files with the fixed answer parser.

Background
----------
``core.prompt.parse_open_answer`` used to fail on markdown-bold answer lines
like ``**Answer: 80**`` (emitted by e.g. gpt-oss-120b). Those correct answers
parsed to ``None`` and were scored wrong, understating GSM8K accuracy badly
(gpt-oss-120b read 67.8% when its true accuracy is ~96%).

The parser is now fixed. This script re-grades every GSM8K result *from the
saved raw model text* — no inference re-run needed — and surgically updates
only the metrics that re-grading can change:

    accuracy, n_correct, accuracy_ci_low/high_95, eats_score, ece,
    accuracy_slm_handled, accuracy_llm_handled

Every resource metric (cost, energy, latency, normalized_*, tokens,
throughput, escalation, confidences, per-tier costs, …) is preserved
byte-for-byte, because re-parsing changes none of them. The accuracy-dependent
metrics are recomputed with the *real* codebase formulas (``wilson_ci``,
``compute_eats``, ``compute_ece``) so the corrected numbers match what a fresh
run would produce.

Per-sample ``correct`` / ``predicted`` / ``final_parsed_answer`` are updated to
reflect the re-parse. Originals are backed up under
``results/_pre_rescore_backup/`` before anything is overwritten.

Usage
-----
    python scripts/rescore_gsm8k.py            # dry run: print what would change
    python scripts/rescore_gsm8k.py --apply    # write corrected json + md (+ backup)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

# Repo root on path so `core`/`evaluation` import when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.prompt import parse_answer
from core.types import ExperimentConfig, ExperimentResult
from evaluation.metrics import compute_ece, compute_eats, wilson_ci
from evaluation.reporter import Reporter

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
BACKUP_DIR = RESULTS_DIR / "_pre_rescore_backup"
NUMERIC_TOL = 1e-9


def _gsm8k_is_correct(pred: str | None, gold: str | None) -> bool:
    """Mirror of benchmarks.gsm8k.GSM8KBenchmark.is_correct."""
    if pred is None or gold is None:
        return False
    try:
        return abs(float(pred.replace(",", "")) - float(gold.replace(",", ""))) < 1e-3
    except ValueError:
        return pred.strip() == gold.strip()


def _config_from_dict(cfg: dict) -> ExperimentConfig:
    fields = ExperimentConfig.__dataclass_fields__
    return ExperimentConfig(**{k: v for k, v in cfg.items() if k in fields})


def rescore_file(path: Path, apply: bool) -> dict | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = data.get("config") or {}
    if cfg.get("benchmark") != "gsm8k":
        return None

    samples = data.get("samples") or []
    if not samples:
        return None

    metrics = data["metrics"]
    n_total = len(samples)

    # --- re-grade each sample from its saved raw text -------------------------
    new_correct: list[bool] = []
    confidences: list[float] = []
    flipped = 0
    for s in samples:
        raw = s.get("final_raw_text") or s.get("final_text") or ""
        gold = s.get("ground_truth")
        new_pred = parse_answer(raw, "open")
        correct = _gsm8k_is_correct(new_pred, gold)
        new_correct.append(correct)
        confidences.append(float(s.get("slm_confidence") or s.get("confidence") or 0.0))
        if correct != bool(s.get("correct")) or new_pred != s.get("predicted"):
            flipped += 1
        # stage the corrected per-sample fields (written only on --apply)
        s["_new_correct"] = correct
        s["_new_pred"] = new_pred

    n_correct = sum(new_correct)
    accuracy = n_correct / n_total

    # --- recompute only the accuracy-dependent metrics ------------------------
    ci_low, ci_high = wilson_ci(n_correct, n_total)
    eats = compute_eats(
        accuracy=accuracy,
        normalized_cost=metrics.get("normalized_cost", 1.0),
        normalized_algorithmic_latency=metrics.get("normalized_algorithmic_latency", 1.0),
        normalized_energy=metrics.get("normalized_energy", 1.0),
    )
    ece = compute_ece(confidences, new_correct)

    escalated = [bool(s.get("escalated")) for s in samples]
    non_esc = [i for i in range(n_total) if not escalated[i]]
    esc = [i for i in range(n_total) if escalated[i]]
    acc_slm = (sum(1 for i in non_esc if new_correct[i]) / len(non_esc)) if non_esc else 0.0
    acc_llm = (sum(1 for i in esc if new_correct[i]) / len(esc)) if esc else 0.0

    old_acc = metrics.get("accuracy", 0.0)
    old_eats = metrics.get("eats_score", 0.0)

    # Only rewrite a run when the parser actually changed a per-sample result.
    # Runs the parser never touched are left byte-for-byte intact — this keeps
    # the script's blast radius exactly equal to the parser bug's, and avoids
    # silently migrating older runs that used a different EATS/ECE definition.
    will_write = flipped > 0

    summary = {
        "file": path.name,
        "experiment_id": data.get("experiment_id"),
        "architecture": cfg.get("architecture"),
        "model": cfg.get("llm") or cfg.get("slm"),
        "n_total": n_total,
        "old_acc": old_acc,
        "new_acc": accuracy,
        "old_correct": int(metrics.get("n_correct", 0)),
        "new_correct": n_correct,
        "recovered": n_correct - int(metrics.get("n_correct", 0)),
        "flipped_samples": flipped,
        "old_eats": old_eats,
        "new_eats": eats,
        "old_ece": metrics.get("ece", 0.0),
        "new_ece": ece,
        "will_write": will_write,
    }

    if not apply or not will_write:
        # discard staging keys so nothing is mutated for skipped/dry runs
        for s in samples:
            s.pop("_new_correct", None)
            s.pop("_new_pred", None)
        return summary

    # --- write corrected metrics in place -------------------------------------
    metrics["accuracy"] = accuracy
    metrics["n_correct"] = float(n_correct)
    metrics["accuracy_ci_low_95"] = ci_low
    metrics["accuracy_ci_high_95"] = ci_high
    metrics["eats_score"] = eats
    metrics["ece"] = ece
    metrics["accuracy_slm_handled"] = acc_slm
    metrics["accuracy_llm_handled"] = acc_llm

    for s in samples:
        s["correct"] = s.pop("_new_correct")
        new_pred = s.pop("_new_pred")
        s["predicted"] = new_pred
        s["final_parsed_answer"] = new_pred

    # back up originals before overwriting
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for ext in (".json", ".md"):
        src = path.with_suffix(ext)
        if src.exists():
            shutil.copy2(src, BACKUP_DIR / src.name)

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # regenerate the .md from the corrected metrics (gsm8k has no subject
    # breakdown, so an empty-sample result reproduces the report faithfully).
    result = ExperimentResult(
        experiment_id=data.get("experiment_id", path.stem),
        config=_config_from_dict(cfg),
        samples=[],
    )
    report_for_md = {"created_at": data.get("completed_at") or data.get("created_at", "")}
    Reporter(RESULTS_DIR)._write_markdown(
        path.with_suffix(".md"), report_for_md, metrics, result, subject_accuracy={}
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()

    files = sorted(RESULTS_DIR.glob("exp_*.json"))
    rows: list[dict] = []
    for f in files:
        try:
            r = rescore_file(f, apply=args.apply)
        except Exception as e:  # noqa: BLE001 — keep going, report at the end
            print(f"  !! {f.name}: {type(e).__name__}: {e}")
            continue
        if r:
            rows.append(r)

    if not rows:
        print("No GSM8K result files found.")
        return

    mode = "APPLIED" if args.apply else "DRY RUN (no files written)"
    print(f"\n=== GSM8K re-score — {mode} ===\n")
    hdr = f"{'':<2}{'experiment':<16}{'arch':<18}{'acc old→new':<20}{'+correct':<10}{'eats old→new':<22}{'ece old→new'}"
    print(hdr)
    print("-" * len(hdr))
    written = [r for r in rows if r["will_write"]]
    skipped = [r for r in rows if not r["will_write"]]
    for r in rows:
        mark = "→" if r["will_write"] else " "
        print(
            f"{mark:<2}"
            f"{r['experiment_id']:<16}"
            f"{str(r['architecture']):<18}"
            f"{r['old_acc']:.3f} → {r['new_acc']:.3f}      "
            f"+{r['recovered']:<9}"
            f"{r['old_eats']:.4f} → {r['new_eats']:.4f}     "
            f"{r['old_ece']:.4f} → {r['new_ece']:.4f}"
        )
    total_recovered = sum(r["recovered"] for r in written)
    verb = "rewritten" if args.apply else "to rewrite"
    print(
        f"\n{len(rows)} GSM8K run(s) scanned · {len(written)} {verb} (parser changed samples) · "
        f"{len(skipped)} untouched · {total_recovered} answer(s) recovered."
    )
    if skipped:
        print(
            "\nNote: '→'-marked rows are the only files modified. Unmarked rows are left\n"
            "untouched. Any eats/ece drift shown for unmarked rows is a pre-existing\n"
            "formula/version difference, NOT a parser change — not migrated here."
        )
    if not args.apply and written:
        print("\nRe-run with --apply to write corrected json + md (originals backed up).")


if __name__ == "__main__":
    main()
