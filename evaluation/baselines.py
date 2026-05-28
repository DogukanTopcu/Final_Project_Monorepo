from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LATENCY_SOURCE_ALGORITHMIC = "algorithmic"


def make_baseline_key(
    benchmark: str,
    n_samples: int,
    seed: int,
    llm: str,
    llm_temperature: float,
    llm_max_tokens: int,
    latency_source: str = LATENCY_SOURCE_ALGORITHMIC,
) -> str:
    return "|".join(
        [
            benchmark,
            str(n_samples),
            str(seed),
            llm,
            f"{llm_temperature:.4f}",
            str(llm_max_tokens),
            latency_source,
        ]
    )


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _index_path(index_path: str | Path) -> Path:
    return Path(index_path)


def _runs_dir(index_path: str | Path) -> Path:
    return _index_path(index_path).parent / "runs"


def list_baselines(index_path: str | Path) -> dict[str, dict[str, Any]]:
    return _load_json(_index_path(index_path), {})


def load_baseline(index_path: str | Path, key: str) -> dict[str, Any] | None:
    index = list_baselines(index_path)
    entry = index.get(key)
    if not isinstance(entry, dict):
        return None
    metrics_path = entry.get("metrics_path")
    if not isinstance(metrics_path, str):
        return None
    run_path = _index_path(index_path).parent / metrics_path
    data = _load_json(run_path, None)
    return data if isinstance(data, dict) else None


def load_recommended_references(path: str | Path) -> dict[str, dict[str, Any]]:
    data = _load_json(Path(path), {})
    return data if isinstance(data, dict) else {}


def baseline_age_days(index_path: str | Path, key: str) -> float | None:
    """Return how many days ago the baseline was saved, or None if not found / no timestamp."""
    index = list_baselines(index_path)
    entry = index.get(key)
    if not isinstance(entry, dict):
        return None
    created_at = entry.get("created_at")
    if not created_at:
        return None
    try:
        saved = datetime.fromisoformat(created_at)
        if saved.tzinfo is None:
            saved = saved.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - saved).total_seconds() / 86400
    except ValueError:
        return None


def is_baseline_stale(
    index_path: str | Path, key: str, max_age_days: float = 7.0
) -> bool:
    """Return True if the baseline is older than max_age_days or missing a timestamp."""
    age = baseline_age_days(index_path, key)
    return age is None or age > max_age_days


def save_baseline(index_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "benchmark",
        "n_samples",
        "seed",
        "llm",
        "llm_temperature",
        "llm_max_tokens",
        "latency_source",
    }
    missing = sorted(key for key in required if key not in payload)
    if missing:
        raise ValueError(f"Missing baseline payload fields: {', '.join(missing)}")

    if "created_at" not in payload:
        payload = {**payload, "created_at": datetime.now(timezone.utc).isoformat()}

    index_file = _index_path(index_path)
    runs_dir = _runs_dir(index_path)
    index_file.parent.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    key = make_baseline_key(
        benchmark=str(payload["benchmark"]),
        n_samples=int(payload["n_samples"]),
        seed=int(payload["seed"]),
        llm=str(payload["llm"]),
        llm_temperature=float(payload["llm_temperature"]),
        llm_max_tokens=int(payload["llm_max_tokens"]),
        latency_source=str(payload.get("latency_source", LATENCY_SOURCE_ALGORITHMIC)),
    )
    baseline_id = str(
        payload.get(
            "baseline_id",
            f"baseline_{payload['benchmark']}_{payload['n_samples']}_{payload['seed']}_{payload['llm']}_{payload['latency_source']}",
        )
    )

    run_filename = f"{baseline_id}.json"
    run_path = runs_dir / run_filename
    run_payload = {**payload, "baseline_id": baseline_id, "baseline_key": key}
    run_path.write_text(json.dumps(run_payload, indent=2))

    index = list_baselines(index_file)
    index[key] = {
        "baseline_id": baseline_id,
        "metrics_path": f"runs/{run_filename}",
        "created_at": payload.get("created_at"),
        "benchmark": payload.get("benchmark"),
        "llm": payload.get("llm"),
        "latency_source": payload.get("latency_source", LATENCY_SOURCE_ALGORITHMIC),
    }
    index_file.write_text(json.dumps(index, indent=2, sort_keys=True))
    return run_payload
