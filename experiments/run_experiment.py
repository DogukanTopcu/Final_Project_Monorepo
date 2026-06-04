"""
CLI entry point for running experiments.

Usage:
    python -m experiments.run_experiment --architecture blackboard --benchmark truthfulqa --n_samples 100
    python -m experiments.run_experiment --config experiments/configs/arch_a.yaml
    python -m experiments.run_experiment --architecture all --benchmark halueval --n_samples 50
"""
from __future__ import annotations

import argparse

from core.types import ExperimentConfig
from experiments.runner import ExperimentRunner


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a thesis experiment")
    p.add_argument("--config", help="Path to YAML config file")
    p.add_argument(
        "--architecture",
        # ADDED: The two new blackboard variants
        choices=[
            "monolithic",
            "routing",
            "multi_agent",
            "active_oracle",
            "ensemble",
            "blackboard",
            "entropy_blackboard",
            "pure_swarm",
            "speculative",
            "dynamic_bidding",
            "all",
        ],
        default="routing",
    )
    p.add_argument(
        "--benchmark",
        choices=[
            # Reasoning benchmarks
            "mmlu", "arc", "hellaswag", "gsm8k", "truthfulqa",
            # Coding benchmarks (execution-based, literature-standard)
            "humaneval_plus", "livecodebench",
            # Deprecated
            "custom_stratified",
        ],
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
    p.add_argument("--max_oracle_calls", type=int, default=3)
    p.add_argument("--n_models", type=int, default=3)
    p.add_argument("--voting", choices=["majority", "weighted"], default="majority")
    p.add_argument("--bid_threshold", type=float, default=0.65)
    p.add_argument("--initial_bid_threshold", type=float, default=0.95)
    p.add_argument("--min_bid_threshold", type=float, default=0.0)
    p.add_argument("--ttl_ms", type=int, default=1500)
    p.add_argument("--max_subtasks", type=int, default=2)
    p.add_argument("--allow_nested_subtasks", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--n_runs",
        type=int,
        default=1,
        help=(
            "Number of independent runs with different seeds (default 1). "
            "Set to 3+ for thesis-grade results (CLAUDE.md §9). "
            "Seeds start from --seed and increment by 1. "
            "Produces a multi-run summary report alongside individual run reports."
        ),
    )
    p.add_argument("--output", default="results")
    p.add_argument("--dry_run", action="store_true")
    p.add_argument(
        "--mlflow_uri",
        default="http://localhost:5000",
        help="MLflow tracking URI",
    )
    return p.parse_args()


def build_config(args: argparse.Namespace, architecture: str) -> ExperimentConfig:
    if architecture in {"blackboard", "entropy_blackboard", "pure_swarm"} and not args.secondary_slm:
        raise ValueError("swarm architectures require --secondary_slm")
    return ExperimentConfig(
        architecture=architecture,
        benchmark=args.benchmark,
        n_samples=args.n_samples,
        slm=None if architecture == "monolithic" else args.slm,
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
        max_oracle_calls=args.max_oracle_calls,
        n_models=args.n_models,
        voting=args.voting,
        bid_threshold=args.bid_threshold,
        initial_bid_threshold=args.initial_bid_threshold,
        min_bid_threshold=args.min_bid_threshold,
        ttl_ms=args.ttl_ms,
        max_subtasks=args.max_subtasks,
        allow_nested_subtasks=args.allow_nested_subtasks,
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
        [
            "monolithic",
            "routing",
            "multi_agent",
            "active_oracle",
            "ensemble",
            "blackboard",
            "entropy_blackboard",
            "pure_swarm",
            "speculative",
            "dynamic_bidding",
        ]
        if args.architecture == "all"
        else [args.architecture]
    )

    if len(architectures) == 1:
        cfg = build_config(args, architectures[0])
        runner = ExperimentRunner(cfg)
        if args.n_runs > 1:
            seeds = list(range(args.seed, args.seed + args.n_runs))
            result = runner.multi_run(n_runs=args.n_runs, seeds=seeds)
            print(
                f"\n[multi-run] {args.n_runs} runs complete. "
                f"accuracy={result['aggregated'].get('accuracy_mean', 0):.3f} "
                f"±{result['aggregated'].get('accuracy_std', 0):.3f}"
            )
        else:
            runner.run()
    else:
        configs = [build_config(args, arch) for arch in architectures]
        ExperimentRunner(configs[0]).batch_run(configs)


if __name__ == "__main__":
    main()
