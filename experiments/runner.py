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
from core.models import assert_model_runnable, get_model
from core.types import ExperimentConfig, ExperimentResult, SampleResult
from evaluation.energy import annotate_response_resource_usage
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
        slm = None
        llm = None
        ensemble_slms: list[Any] = []

        # Determine which models this architecture needs.
        if cfg.architecture == "monolithic":
            assert_model_runnable(cfg.llm)
            llm = get_model(cfg.llm)
        elif cfg.architecture == "ensemble":
            ensemble_ids = cfg.ensemble_slms or ([cfg.slm] if cfg.slm else [])
            if not ensemble_ids:
                raise ValueError("ensemble requires at least one SLM (set ensemble_slms or slm).")
            for sid in ensemble_ids:
                assert_model_runnable(sid)
                ensemble_slms.append(get_model(sid))
            if cfg.llm_tiebreak and cfg.llm:
                assert_model_runnable(cfg.llm)
                llm = get_model(cfg.llm)
        else:
            # routing, multi_agent, multi_agent_crew, speculative
            assert_model_runnable(cfg.slm)
            assert_model_runnable(cfg.llm)
            slm = get_model(cfg.slm)
            llm = get_model(cfg.llm)

        # Build architecture kwargs
        arch_kwargs: dict[str, Any] = {}
        if slm is not None:
            arch_kwargs["slm"] = slm
        if llm is not None:
            arch_kwargs["llm"] = llm
        if ensemble_slms:
            arch_kwargs["slms"] = ensemble_slms

        arch_kwargs["slm_temperature"] = cfg.slm_temperature
        arch_kwargs["llm_temperature"] = cfg.llm_temperature
        arch_kwargs["slm_max_tokens"] = cfg.slm_max_tokens
        arch_kwargs["llm_max_tokens"] = cfg.llm_max_tokens

        if cfg.architecture == "routing":
            arch_kwargs["confidence_threshold"] = cfg.confidence_threshold
        elif cfg.architecture == "multi_agent":
            arch_kwargs["arbitrator"] = cfg.arbitrator
            arch_kwargs["n_rounds"] = cfg.n_debate_rounds
        elif cfg.architecture == "ensemble":
            arch_kwargs["n_models"] = cfg.n_models
            arch_kwargs["voting"] = cfg.voting
            arch_kwargs["llm_tiebreak"] = cfg.llm_tiebreak
        elif cfg.architecture == "speculative":
            arch_kwargs["acceptance_threshold"] = cfg.speculative_acceptance_threshold

        benchmark = get_benchmark(cfg.benchmark, n_samples=cfg.n_samples, seed=cfg.seed)
        arch_kwargs["task_type"] = benchmark.task_type
        architecture = get_architecture(cfg.architecture, **arch_kwargs)

        queries = benchmark.load()
        result = ExperimentResult(experiment_id=self.experiment_id, config=cfg)

        if cfg.architecture == "monolithic":
            pair_label = f"(LLM only) {cfg.llm}"
        elif cfg.architecture == "ensemble" and (cfg.ensemble_slms or not cfg.slm):
            members = cfg.ensemble_slms or [cfg.slm or "?"]
            tiebreak = f" → tiebreak {cfg.llm}" if (cfg.llm_tiebreak and cfg.llm) else ""
            pair_label = f"ensemble[{', '.join(members)}]{tiebreak}"
        else:
            pair_label = f"{cfg.slm or '?'} → {cfg.llm or '?'}"
        print(
            f"[{self.experiment_id}] {cfg.architecture} | {cfg.benchmark} | "
            f"{pair_label} | {len(queries)} samples"
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
            primary_id = cfg.llm if cfg.architecture == "monolithic" else (cfg.slm or cfg.llm or "model")
            tracker.start_run(
                run_name=f"{primary_id}-{cfg.benchmark}-{cfg.n_samples}",
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

            response = annotate_response_resource_usage(response)
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
                    f"cost=${result.total_cost_usd:.4f} "
                    f"energy={result.total_energy_kwh:.4f}kWh"
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
