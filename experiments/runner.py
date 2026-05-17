"""
ExperimentRunner
================
Orchestrates the full experiment loop:
  1. Load benchmark queries
  2. Build architecture with configured models
  3. Run each query, collecting Response objects
  4. Score responses against ground truth
  5. Log to MLflow (optional)
  6. Save JSON + Markdown reports
  7. Invoke RunnerCallbacks for SSE streaming (Web UI integration)

Designed to run in a ThreadPoolExecutor — all state is local, no global mutation.
"""
from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from architectures import get_architecture
from benchmarks import get_benchmark
from core.config import load_config
from core.models import get_model
from core.types import ExperimentConfig, ExperimentResult, SampleResult
from evaluation.metrics import compute_metrics
from evaluation.reporter import Reporter


class ExperimentCancelledError(RuntimeError):
    """Raised when a caller requests cancellation mid-run."""


class ExperimentRunner:
    def __init__(
        self,
        config: ExperimentConfig,
        callbacks=None,   # mlops.callbacks.RunnerCallbacks | None
    ) -> None:
        self.config = config
        self.callbacks = callbacks
        self.experiment_id = f"exp_{uuid.uuid4().hex[:8]}"

    @classmethod
    def from_yaml(cls, path: str | Path, **overrides) -> ExperimentRunner:
        config = load_config(path)
        for k, v in overrides.items():
            if hasattr(config, k):
                setattr(config, k, v)
        return cls(config)

    def run(self) -> ExperimentResult:
        cfg = self.config

        # Dry run — validate config, skip inference
        if cfg.dry_run:
            print(f"[DRY RUN] {self.experiment_id} config validated. No inference.")
            return ExperimentResult(
                experiment_id=self.experiment_id,
                config=cfg,
                samples=[],
            )

        # Build models
        slm = get_model(cfg.slm)
        llm = get_model(cfg.llm)

        # Build architecture
        arch_kwargs: dict[str, Any] = {
            "slm": slm,
            "llm": llm,
        }
        if cfg.architecture == "routing":
            arch_kwargs["confidence_threshold"] = cfg.confidence_threshold
        elif cfg.architecture == "multi_agent":
            arch_kwargs["arbitrator"] = cfg.arbitrator
            arch_kwargs["n_rounds"] = cfg.n_debate_rounds
        elif cfg.architecture == "ensemble":
            arch_kwargs["n_models"] = cfg.n_models
            arch_kwargs["voting"] = cfg.voting

        benchmark = get_benchmark(cfg.benchmark, n_samples=cfg.n_samples, seed=cfg.seed)
        arch_kwargs["task_type"] = benchmark.task_type
        architecture = get_architecture(cfg.architecture, **arch_kwargs)

        queries = benchmark.load()
        result = ExperimentResult(experiment_id=self.experiment_id, config=cfg)

        print(
            f"[{self.experiment_id}] {cfg.architecture} | {cfg.benchmark} | "
            f"{cfg.slm} → {cfg.llm} | {len(queries)} samples"
        )

        # MLflow tracking
        tracker = None
        final_metrics = result.to_metrics()
        try:
            from mlops.tracking import MLflowTracker
            import dataclasses
            tracker = MLflowTracker(
                experiment_name=f"thesis-{cfg.architecture}",
                tracking_uri=cfg.mlflow_tracking_uri,
            )
            tracker.start_run(
                run_name=f"{cfg.slm}-{cfg.benchmark}-{cfg.n_samples}",
                config=dataclasses.asdict(cfg),
            )
        except Exception as e:
            print(f"[WARN] MLflow not available: {e}")

        for i, query in enumerate(queries, start=1):
            if self.callbacks and self.callbacks.is_cancelled():
                if tracker:
                    tracker.end_run("KILLED")
                raise ExperimentCancelledError("Experiment cancelled by user.")

            try:
                response = architecture.run(query)
            except Exception as exc:
                if self.callbacks:
                    self.callbacks.error(exc)
                if tracker:
                    tracker.end_run("FAILED")
                raise

            correct = benchmark.is_correct(response.predicted_answer, query)
            sample = SampleResult(query=query, response=response, correct=correct)
            result.samples.append(sample)

            if tracker:
                try:
                    tracker.log_sample(query.id, response.text, correct, response)
                except Exception:
                    pass

            if self.callbacks:
                self.callbacks.sample_complete(i, len(queries), response)
                running_acc = result.n_correct / i
                self.callbacks.metric_update("accuracy", running_acc)
                self.callbacks.metric_update("llm_call_ratio", result.llm_call_ratio)

            if i % 10 == 0 or i == len(queries):
                print(
                    f"  [{i}/{len(queries)}] acc={result.accuracy:.3f} "
                    f"llm_ratio={result.llm_call_ratio:.3f} "
                    f"cost=${result.total_cost_usd:.4f}"
                )

        # Save reports
        reporter = Reporter(output_dir=cfg.output_dir)
        reporter.save(result)
        final_metrics = compute_metrics(result)

        if tracker:
            try:
                tracker.log_final_metrics(final_metrics)
                tracker.log_artifacts(Path(cfg.output_dir))
                tracker.end_run()
            except Exception:
                pass

        if self.callbacks:
            from mlops.callbacks import ExperimentResult as CallbackResult
            cb_result = CallbackResult(
                experiment_id=self.experiment_id,
                architecture=cfg.architecture,
                benchmark=cfg.benchmark,
                metrics=final_metrics,
                samples_processed=result.n_total,
                status="completed",
            )
            self.callbacks.experiment_done(cb_result)

        print(
            f"[{self.experiment_id}] DONE — acc={result.accuracy:.3f} "
            f"eats={final_metrics.get('eats_score', 0):.3f}"
        )
        return result

    def batch_run(self, configs: list[ExperimentConfig], max_workers: int = 4) -> list[ExperimentResult]:
        """Run multiple experiments in parallel."""
        results: list[ExperimentResult] = []
        runners = [ExperimentRunner(cfg) for cfg in configs]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(r.run): r for r in runners}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    print(f"[ERROR] {exc}")

        return results
