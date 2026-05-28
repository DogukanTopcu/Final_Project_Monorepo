from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from analysis.monolithic_llm_sweep import find_matching_results, load_manifest


def config_payload(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "architecture": "monolithic",
        "benchmark": run["benchmark"],
        "n_samples": int(run["n_samples"]),
        "llm": run["llm"],
        "seed": int(run["seed"]),
        "slm": None,
        "slm_temperature": 0.0,
        "llm_temperature": float(run["llm_temperature"]),
        "slm_max_tokens": 0,
        "llm_max_tokens": int(run["llm_max_tokens"]),
        "slm_only": False,
        "output_dir": run["output_dir"],
    }


def write_configs(runs: list[dict[str, Any]], output_dir: str | Path) -> list[Path]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for run in runs:
        path = out_dir / f"{run['run_id']}.yaml"
        path.write_text(yaml.safe_dump(config_payload(run), sort_keys=False))
        paths.append(path)
    return paths


def build_commands(config_paths: list[Path]) -> list[str]:
    return [f"python -m experiments.run_experiment --config '{path}'" for path in config_paths]


def build_status_rows(runs: list[dict[str, Any]], results_dir: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in runs:
        matches = find_matching_results(run, results_dir)
        rows.append(
            {
                "run_id": run["run_id"],
                "benchmark": run["benchmark"],
                "llm": run["llm"],
                "model_class": run["model_class"],
                "status": "completed" if matches else "pending",
                "matching_results": len(matches),
                "latest_result": str(matches[-1]) if matches else "",
            }
        )
    return rows


def render_status_table(rows: list[dict[str, Any]]) -> str:
    headers = ["run_id", "benchmark", "llm", "model_class", "status", "matching_results", "latest_result"]
    widths = {header: len(header) for header in headers}
    for row in rows:
        for header in headers:
            widths[header] = max(widths[header], len(str(row.get(header, ""))))
    lines = [
        " | ".join(header.ljust(widths[header]) for header in headers),
        "-+-".join("-" * widths[header] for header in headers),
    ]
    for row in rows:
        lines.append(" | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare manual monolithic LLM sweep execution")
    parser.add_argument("--manifest", default="experiments/manifests/monolithic_llm_sweep.yaml")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument(
        "--config-dir",
        default="experiments/generated/monolithic_llm_sweep",
    )
    args = parser.parse_args()

    runs = load_manifest(args.manifest)
    config_paths = write_configs(runs, args.config_dir)
    commands = build_commands(config_paths)
    status_rows = build_status_rows(runs, args.results_dir)

    print("# Commands")
    for command in commands:
        print(command)
    print("\n# Status")
    print(render_status_table(status_rows))


if __name__ == "__main__":
    main()
