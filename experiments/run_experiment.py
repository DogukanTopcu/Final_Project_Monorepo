"""
CLI entry point for running experiments.

Usage:
    python -m experiments.run_experiment --architecture routing --benchmark mmlu --n_samples 100
    python -m experiments.run_experiment --config experiments/configs/arch_a.yaml
    python -m experiments.run_experiment --architecture all --benchmark mmlu --n_samples 50
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.types import ExperimentConfig
from experiments.runner import ExperimentRunner


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a thesis experiment")
    p.add_argument("--config", help="Path to YAML config file")
    p.add_argument(
        "--architecture",
        choices=["routing", "multi_agent", "ensemble", "all"],
        default="routing",
    )
    p.add_argument(
        "--benchmark",
        choices=["mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa"],
        default="mmlu",
    )
    p.add_argument("--n_samples", type=int, default=100)
    p.add_argument("--slm", default="qwen3.5-4b")
    p.add_argument("--llm", default="llama3.3-70b")
    p.add_argument("--confidence_threshold", type=float, default=0.7)
    p.add_argument("--arbitrator", choices=["slm", "llm"], default="slm")
    p.add_argument("--n_models", type=int, default=3)
    p.add_argument("--voting", choices=["majority", "weighted"], default="majority")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--output", default="results")
    p.add_argument("--dry_run", action="store_true")
    p.add_argument(
        "--mlflow_uri",
        default="http://localhost:5000",
        help="MLflow tracking URI",
    )
    return p.parse_args()


def build_config(args: argparse.Namespace, architecture: str) -> ExperimentConfig:
    return ExperimentConfig(
        architecture=architecture,
        benchmark=args.benchmark,
        n_samples=args.n_samples,
        slm=args.slm,
        llm=args.llm,
        confidence_threshold=args.confidence_threshold,
        arbitrator=args.arbitrator,
        n_models=args.n_models,
        voting=args.voting,
        dry_run=args.dry_run,
        seed=args.seed,
        output_dir=args.output,
        mlflow_tracking_uri=args.mlflow_uri,
    )


def main() -> None:
    args = parse_args()

    if args.config:
        runner = ExperimentRunner.from_yaml(args.config)
        runner.run()
        return

    architectures = (
        ["routing", "multi_agent", "ensemble"]
        if args.architecture == "all"
        else [args.architecture]
    )

    if len(architectures) == 1:
        cfg = build_config(args, architectures[0])
        ExperimentRunner(cfg).run()
    else:
        configs = [build_config(args, arch) for arch in architectures]
        ExperimentRunner(configs[0]).batch_run(configs)


if __name__ == "__main__":
    main()
