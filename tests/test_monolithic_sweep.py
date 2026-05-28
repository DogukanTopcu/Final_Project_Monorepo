from __future__ import annotations

import json
import sys
from pathlib import Path

from analysis.monolithic_llm_sweep import (
    compute_llm_benchmark_scores,
    extract_summary_row,
    load_manifest,
    result_matches_run,
    select_recommended_dense_references,
)
from evaluation.baselines import (
    LATENCY_SOURCE_ALGORITHMIC,
    load_baseline,
    make_baseline_key,
    save_baseline,
)
from experiments.monolithic_sweep_helper import build_commands, build_status_rows, write_configs
from experiments.run_experiment import build_config, parse_args


def test_cli_accepts_monolithic_architecture(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_experiment.py",
            "--architecture",
            "monolithic",
            "--benchmark",
            "mmlu",
            "--llm",
            "gpt-oss-20b",
        ],
    )
    args = parse_args()
    cfg = build_config(args, "monolithic")
    assert cfg.architecture == "monolithic"
    assert cfg.slm is None
    assert cfg.llm == "gpt-oss-20b"


def test_manifest_contains_expected_35_runs():
    runs = load_manifest("experiments/manifests/monolithic_llm_sweep.yaml")
    assert len(runs) == 35
    assert all(run["architecture"] == "monolithic" for run in runs)


def test_helper_emits_35_commands_and_writes_configs(tmp_path: Path):
    runs = load_manifest("experiments/manifests/monolithic_llm_sweep.yaml")
    config_paths = write_configs(runs, tmp_path / "configs")
    commands = build_commands(config_paths)
    assert len(config_paths) == 35
    assert len(commands) == 35
    assert commands[0].startswith("python -m experiments.run_experiment --config ")


def test_baseline_registry_roundtrip(tmp_path: Path):
    index_path = tmp_path / "artifacts" / "baselines" / "index.json"
    payload = {
        "benchmark": "mmlu",
        "n_samples": 1000,
        "seed": 42,
        "llm": "gemma4-31b",
        "llm_temperature": 0.0,
        "llm_max_tokens": 0,
        "latency_source": LATENCY_SOURCE_ALGORITHMIC,
        "accuracy": 0.82,
        "avg_algorithmic_latency_ms": 123.0,
        "avg_latency_ms": 150.0,
        "total_cost_usd": 1.2,
        "total_energy_kwh": 0.4,
        "total_co2_g": 12.0,
        "created_at": "2026-05-27T00:00:00Z",
    }
    saved = save_baseline(index_path, payload)
    key = make_baseline_key(
        benchmark="mmlu",
        n_samples=1000,
        seed=42,
        llm="gemma4-31b",
        llm_temperature=0.0,
        llm_max_tokens=0,
    )
    loaded = load_baseline(index_path, key)
    assert saved["baseline_key"] == key
    assert loaded is not None
    assert loaded["accuracy"] == 0.82
    assert loaded["avg_algorithmic_latency_ms"] == 123.0


def test_result_matching_and_status_detection(tmp_path: Path):
    run = {
        "run_id": "monolithic_gpt-oss-20b_mmlu",
        "architecture": "monolithic",
        "benchmark": "mmlu",
        "llm": "gpt-oss-20b",
        "model_family": "GPT OSS",
        "model_class": "dense_llm",
        "n_samples": 1000,
        "seed": 42,
        "llm_temperature": 0.0,
        "llm_max_tokens": 0,
        "output_dir": "results",
    }
    result_payload = {
        "experiment_id": "exp_test",
        "created_at": "2026-05-27T00:00:00Z",
        "config": {
            "architecture": "monolithic",
            "benchmark": "mmlu",
            "llm": "gpt-oss-20b",
            "n_samples": 1000,
            "seed": 42,
            "llm_temperature": 0.0,
            "llm_max_tokens": 0,
        },
        "metrics": {},
    }
    result_path = tmp_path / "exp_test.json"
    result_path.write_text(json.dumps(result_payload))

    assert result_matches_run(result_payload, run) is True
    rows = build_status_rows([run], tmp_path)
    assert rows[0]["status"] == "completed"
    assert rows[0]["matching_results"] == 1


def test_extract_summary_row_and_recommendation(tmp_path: Path):
    run_dense = {
        "run_id": "dense",
        "architecture": "monolithic",
        "benchmark": "mmlu",
        "llm": "gemma4-31b",
        "model_family": "Gemma",
        "model_class": "dense_llm",
        "n_samples": 1000,
        "seed": 42,
        "llm_temperature": 0.0,
        "llm_max_tokens": 0,
        "output_dir": "results",
    }
    run_moe = {**run_dense, "run_id": "moe", "llm": "gemma4-26b-a4b", "model_class": "moe"}
    dense_result = {
        "experiment_id": "exp_dense",
        "created_at": "2026-05-27T00:00:00Z",
        "config": {
            "architecture": "monolithic",
            "benchmark": "mmlu",
            "llm": "gemma4-31b",
            "n_samples": 1000,
            "seed": 42,
            "llm_temperature": 0.0,
            "llm_max_tokens": 0,
        },
        "metrics": {
            "accuracy": 0.9,
            "avg_algorithmic_latency_ms": 100.0,
            "avg_latency_ms": 130.0,
            "total_cost_usd": 1.2,
            "total_energy_kwh": 0.4,
            "total_co2_g": 10.0,
        },
    }
    moe_result = {
        "experiment_id": "exp_moe",
        "created_at": "2026-05-27T00:00:00Z",
        "config": {
            "architecture": "monolithic",
            "benchmark": "mmlu",
            "llm": "gemma4-26b-a4b",
            "n_samples": 1000,
            "seed": 42,
            "llm_temperature": 0.0,
            "llm_max_tokens": 0,
        },
        "metrics": {
            "accuracy": 0.85,
            "avg_algorithmic_latency_ms": 80.0,
            "avg_latency_ms": 100.0,
            "total_cost_usd": 0.9,
            "total_energy_kwh": 0.3,
            "total_co2_g": 8.0,
        },
    }
    dense_path = tmp_path / "dense.json"
    moe_path = tmp_path / "moe.json"
    dense_path.write_text(json.dumps(dense_result))
    moe_path.write_text(json.dumps(moe_result))

    dense_row = extract_summary_row(run_dense, dense_path)
    moe_row = extract_summary_row(run_moe, moe_path)
    scored = compute_llm_benchmark_scores([dense_row, moe_row])
    refs = select_recommended_dense_references(scored)

    assert len(scored) == 2
    assert all("llm_benchmark_score" in row for row in scored)
    assert refs["mmlu"]["llm"] == "gemma4-31b"
    assert refs["mmlu"]["model_class"] == "dense_llm"
