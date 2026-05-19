"""
CLI entry point for running experiments.

Usage:
    python -m experiments.run_experiment --architecture blackboard --benchmark truthfulqa --n_samples 100
    python -m experiments.run_experiment --config experiments/configs/arch_a.yaml
    python -m experiments.run_experiment --architecture all --benchmark halueval --n_samples 50
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
        # ADDED: The two new blackboard variants
        choices=["routing", "multi_agent", "ensemble", "blackboard", "entropy_blackboard", "all"],
        default="routing",
    )
    p.add_argument(
        "--benchmark",
        # ADDED: halueval for hallucination detection
        choices=["mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa", "halueval"],
        default="mmlu",
    )
    p.add_argument("--n_samples", type=int, default=100)
    p.add_argument("--slm", default="qwen3.5-4b")
    # Secondary SLM for swarm architectures
    p.add_argument("--secondary_slm", default=None)
    p.add_argument("--llm", default="llama3.3-70b")
    p.add_argument("--slm_temperature", type=float, default=0.0)
    p.add_argument("--llm_temperature", type=float, default=0.0)
    p.add_argument(
        "--slm_max_tokens",
        type=int,
        default=0,
        help="0 = auto budget; positive values override completion budget explicitly.",
    )
    p.add_argument(
        "--llm_max_tokens",
        type=int,
        default=0,
        help="0 = auto budget; positive values override completion budget explicitly.",
    )
    p.add_argument("--slm_only", action="store_true")
    p.add_argument("--confidence_threshold", type=float, default=0.7)
    p.add_argument("--margin_threshold", type=float)
    p.add_argument("--long-input-token-threshold", dest="long_input_token_threshold", type=int)
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
    if architecture in {"blackboard", "entropy_blackboard"} and not args.secondary_slm:
        raise ValueError("blackboard architectures require --secondary_slm")
    return ExperimentConfig(
        architecture=architecture,
        benchmark=args.benchmark,
        n_samples=args.n_samples,
        slm=args.slm,
        secondary_slm=args.secondary_slm,
        llm=args.llm,
        slm_temperature=args.slm_temperature,
        llm_temperature=args.llm_temperature,
        slm_max_tokens=args.slm_max_tokens,
        llm_max_tokens=args.llm_max_tokens,
        slm_only=args.slm_only,
        confidence_threshold=args.confidence_threshold,
        margin_threshold=args.margin_threshold,
        long_input_token_threshold=args.long_input_token_threshold,
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
        ["routing", "multi_agent", "ensemble", "blackboard", "entropy_blackboard"]
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