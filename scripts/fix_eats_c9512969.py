"""One-off: bring exp_c9512969's EATS onto the current formula.

This run was written by an older harness that stored eats_score with a
deprecated formula and left normalized_algorithmic_latency / normalized_energy /
normalized_efficiency_penalty as None. It is a monolithic GSM8K baseline, so all
three normalized components are 1.0 by definition. Recompute EATS with the
current `compute_eats` and fill the missing normalized fields so the report is
self-consistent. Accuracy and all resource metrics are untouched.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.types import ExperimentConfig, ExperimentResult
from evaluation.metrics import compute_eats
from evaluation.reporter import Reporter

RESULTS = Path(__file__).resolve().parent.parent / "results"
BACKUP = RESULTS / "_pre_rescore_backup"
EID = "exp_c9512969"


def main() -> None:
    path = RESULTS / f"{EID}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    m = data["metrics"]

    # Monolithic baseline → every normalized component is 1.0.
    nc = m.get("normalized_cost") if m.get("normalized_cost") is not None else 1.0
    nl = 1.0
    ne = 1.0
    penalty = 0.5 * nc + 0.3 * nl + 0.2 * ne
    eats = compute_eats(
        accuracy=m["accuracy"],
        normalized_cost=nc,
        normalized_algorithmic_latency=nl,
        normalized_energy=ne,
    )

    print(f"eats_score: {m.get('eats_score')} -> {eats}")
    print(f"normalized_algorithmic_latency: {m.get('normalized_algorithmic_latency')} -> {nl}")
    print(f"normalized_energy: {m.get('normalized_energy')} -> {ne}")
    print(f"normalized_efficiency_penalty: {m.get('normalized_efficiency_penalty')} -> {penalty}")

    m["normalized_cost"] = nc
    m["normalized_algorithmic_latency"] = nl
    m["normalized_energy"] = ne
    m["normalized_efficiency_penalty"] = penalty
    m["eats_score"] = eats

    BACKUP.mkdir(parents=True, exist_ok=True)
    for ext in (".json", ".md"):
        src = path.with_suffix(ext)
        if src.exists() and not (BACKUP / src.name).exists():
            shutil.copy2(src, BACKUP / src.name)

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    cfg = data["config"]
    fields = ExperimentConfig.__dataclass_fields__
    result = ExperimentResult(
        experiment_id=EID,
        config=ExperimentConfig(**{k: v for k, v in cfg.items() if k in fields}),
        samples=[],
    )
    report_for_md = {"created_at": data.get("completed_at") or data.get("created_at", "")}
    Reporter(RESULTS)._write_markdown(
        path.with_suffix(".md"), report_for_md, m, result, subject_accuracy={}
    )
    print("written:", path.name, "+ .md (original backed up)")


if __name__ == "__main__":
    main()
