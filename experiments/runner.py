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

Queries run one at a time (the GPU serves a single request, so the recorded
wall-clock latency — and the energy derived from it — reflects isolated
execution). A single background thread handles the non-GPU post-processing
(scoring, energy annotation, MLflow, callbacks) so that bookkeeping overlaps
the next request instead of blocking the run.
"""
from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue
from typing import Any

from architectures import get_architecture
from benchmarks import get_benchmark
from core.config import load_config
from core.models import assert_model_runnable, get_model
from core.types import ExperimentConfig, ExperimentResult, SampleResult
from evaluation.baselines import load_recommended_references
from evaluation.energy import annotate_response_resource_usage
from evaluation.metrics import aggregate_runs, compute_metrics
from evaluation.reporter import Reporter


def resolve_recommended_baseline(benchmark: str, llm: str | None = None, n_samples: int | None = None) -> dict[str, float]:
    """Load the monolithic baseline metrics for a benchmark and optionally a specific LLM.

    Standalone function (not tied to a runner instance) so the experiment
    service can import and call it directly without depending on ExperimentRunner.
    """
    from evaluation.baselines import list_baselines, load_baseline
    
    scale_factor = (n_samples / 500.0) if n_samples else 1.0

    if llm:
        index_path = Path("artifacts/baselines/index.json")
        index = list_baselines(index_path)
        for k, v in index.items():
            if v.get("benchmark") == benchmark and v.get("llm") == llm:
                run_data = load_baseline(index_path, k)
                if run_data:
                    acc = run_data.get("accuracy")
                    eats = (acc / (acc + 1.0)) if acc is not None else None
                    return {
                        "total_cost_usd": float(run_data.get("total_cost_usd", 0.0) or 0.0) * scale_factor,
                        "avg_algorithmic_latency_ms": float(run_data.get("avg_algorithmic_latency_ms") or run_data.get("avg_latency_ms") or 0.0),
                        "total_energy_kwh": float(run_data.get("total_energy_kwh", 0.0) or 0.0) * scale_factor,
                        "accuracy": acc,
                        "eats_score": eats,
                        "ece": run_data.get("ece"),
                    }

    # Fallback to average of all LLMs for this benchmark
    path = Path(__file__).parent.parent / "monolithic_constants.json"
    if not path.exists():
        return {}
        
    import json
    with open(path, "r") as f:
        constants = json.load(f)
    
    benchmark_data = constants.get(benchmark, {})
    if not benchmark_data:
        return {}
        
    models = list(benchmark_data.values())
    n_models = len(models)
    
    avg_cost = sum(m.get("total_cost_usd", 0.0) or 0.0 for m in models) / n_models
    
    avg_latency = 0.0
    for m in models:
        lat = m.get("avg_algorithmic_latency_ms")
        if lat is None:
            lat = m.get("avg_latency_ms", 0.0)
        avg_latency += (lat or 0.0)
    avg_latency /= n_models
    
    avg_energy = sum(m.get("total_energy_kwh", 0.0) or 0.0 for m in models) / n_models
    avg_acc = sum(m.get("accuracy", 0.0) or 0.0 for m in models) / n_models
    avg_ece = sum(m.get("ece", 0.0) or 0.0 for m in models) / n_models
    eats = avg_acc / (avg_acc + 1.0)
    
    return {
        "total_cost_usd": avg_cost * scale_factor,
        "avg_algorithmic_latency_ms": avg_latency,
        "total_energy_kwh": avg_energy * scale_factor,
        "accuracy": avg_acc,
        "eats_score": eats,
        "ece": avg_ece,
    }


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

    # ------------------------------------------------------------------
    # Architecture factory helpers
    # ------------------------------------------------------------------

    def _validate_models(self, cfg: ExperimentConfig) -> None:
        """Call assert_model_runnable once for every model this run needs."""
        if cfg.architecture == "monolithic":
            assert_model_runnable(cfg.llm)
        elif cfg.architecture in {"ensemble", "dynamic_bidding"}:
            ensemble_ids = cfg.ensemble_slms or (
                [cfg.slm] * max(int(cfg.n_models), 1) if cfg.slm else []
            )
            for sid in ensemble_ids:
                assert_model_runnable(sid)
            if cfg.architecture == "ensemble" and cfg.llm_tiebreak and cfg.llm:
                assert_model_runnable(cfg.llm)
        elif cfg.architecture in {"blackboard", "entropy_blackboard"}:
            assert_model_runnable(cfg.slm)
            assert_model_runnable(cfg.llm)
            if not cfg.secondary_slm:
                raise ValueError(f"{cfg.architecture} requires secondary_slm")
            assert_model_runnable(cfg.secondary_slm)
        elif cfg.architecture == "pure_swarm":
            assert_model_runnable(cfg.slm)
            if not cfg.secondary_slm:
                raise ValueError("pure_swarm requires secondary_slm")
            assert_model_runnable(cfg.secondary_slm)
        else:
            assert_model_runnable(cfg.slm)
            assert_model_runnable(cfg.llm)

    def _build_arch(self, cfg: ExperimentConfig, task_type: str) -> Any:
        """Create one independent architecture instance with its own model clients.

        Called once per worker so threads never share mutable model state.
        get_model() is cheap (creates an HTTP client wrapper, no GPU weights).
        """
        slm = None
        secondary_slm = None
        llm = None
        ensemble_slms: list[Any] = []

        if cfg.architecture == "monolithic":
            llm = get_model(cfg.llm)
        elif cfg.architecture in {"ensemble", "dynamic_bidding"}:
            ensemble_ids = cfg.ensemble_slms or (
                [cfg.slm] * max(int(cfg.n_models), 1) if cfg.slm else []
            )
            if not ensemble_ids:
                raise ValueError(f"{cfg.architecture} requires at least one SLM.")
            ensemble_slms = [get_model(sid) for sid in ensemble_ids]
            if cfg.architecture == "ensemble" and cfg.llm_tiebreak and cfg.llm:
                llm = get_model(cfg.llm)
        elif cfg.architecture in {"blackboard", "entropy_blackboard"}:
            slm = get_model(cfg.slm)
            secondary_slm = get_model(cfg.secondary_slm)
            llm = get_model(cfg.llm)
        elif cfg.architecture == "pure_swarm":
            slm = get_model(cfg.slm)
            secondary_slm = get_model(cfg.secondary_slm)
        else:
            slm = get_model(cfg.slm)
            llm = get_model(cfg.llm)

        arch_kwargs: dict[str, Any] = {"task_type": task_type}
        if slm is not None:
            arch_kwargs["slm"] = slm
        if llm is not None:
            arch_kwargs["llm"] = llm
        if ensemble_slms:
            arch_kwargs["slms"] = ensemble_slms
        if cfg.architecture in {"blackboard", "entropy_blackboard"}:
            arch_kwargs["secondary_slm"] = secondary_slm
            arch_kwargs["cost_weight"] = getattr(cfg, "cost_weight", 0.15)
            arch_kwargs["bid_threshold"] = getattr(cfg, "bid_threshold", 0.65)
            arch_kwargs["ttl_ms"] = getattr(cfg, "ttl_ms", 1500)
            arch_kwargs["max_subtasks"] = getattr(cfg, "max_subtasks", 2)
        if cfg.architecture == "entropy_blackboard":
            arch_kwargs["entropy_weight"] = getattr(cfg, "entropy_weight", 0.5)
            arch_kwargs["top_k"] = getattr(cfg, "entropy_top_k", 20)
        if cfg.architecture == "pure_swarm":
            arch_kwargs["secondary_slm"] = secondary_slm
            arch_kwargs["cost_weight"] = getattr(cfg, "cost_weight", 0.15)
            arch_kwargs["bid_threshold"] = getattr(cfg, "bid_threshold", 0.65)
            arch_kwargs["ttl_ms"] = getattr(cfg, "ttl_ms", 1500)
            arch_kwargs["max_subtasks"] = getattr(cfg, "max_subtasks", 2)
            arch_kwargs["allow_nested_subtasks"] = getattr(cfg, "allow_nested_subtasks", False)

        arch_kwargs["slm_temperature"] = cfg.slm_temperature
        arch_kwargs["slm_max_tokens"] = cfg.slm_max_tokens
        if llm is not None:
            arch_kwargs["llm_temperature"] = cfg.llm_temperature
            arch_kwargs["llm_max_tokens"] = cfg.llm_max_tokens

        if cfg.architecture == "routing":
            arch_kwargs["slm_only"] = cfg.slm_only
            arch_kwargs["confidence_threshold"] = cfg.confidence_threshold
            arch_kwargs["margin_threshold"] = cfg.margin_threshold
            arch_kwargs["long_input_token_threshold"] = cfg.long_input_token_threshold
            arch_kwargs["force_escalate"] = cfg.force_escalate
            arch_kwargs["confidence_method"] = cfg.confidence_method
        elif cfg.architecture == "multi_agent":
            arch_kwargs["arbitrator"] = cfg.arbitrator
            arch_kwargs["n_rounds"] = getattr(cfg, "n_debate_rounds", 3)
        elif cfg.architecture == "ensemble":
            arch_kwargs["n_models"] = cfg.n_models
            arch_kwargs["voting"] = cfg.voting
            arch_kwargs["llm_tiebreak"] = cfg.llm_tiebreak
        elif cfg.architecture == "dynamic_bidding":
            arch_kwargs["cost_weight"] = getattr(cfg, "cost_weight", 0.15)
            arch_kwargs["initial_bid_threshold"] = getattr(cfg, "initial_bid_threshold", 0.90)
            arch_kwargs["min_bid_threshold"] = getattr(cfg, "min_bid_threshold", 0.10)
            arch_kwargs["ttl_ms"] = getattr(cfg, "ttl_ms", 1500)
        elif cfg.architecture == "active_oracle":
            arch_kwargs["max_oracle_calls"] = cfg.max_oracle_calls
        elif cfg.architecture == "speculative":
            arch_kwargs["acceptance_threshold"] = getattr(cfg, "speculative_acceptance_threshold", 0.8)
            arch_kwargs["draft_max_tokens"] = getattr(cfg, "speculative_max_draft_tokens", 64)

        return get_architecture(cfg.architecture, **arch_kwargs)

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------

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

        # Validate model availability once before running any query.
        self._validate_models(cfg)

        benchmark = get_benchmark(cfg.benchmark, n_samples=cfg.n_samples, seed=cfg.seed)
        queries = benchmark.load()
        result = ExperimentResult(experiment_id=self.experiment_id, config=cfg)

        # One architecture instance. Queries run one at a time so the GPU only
        # ever serves a single request and the wall-clock latency we record
        # (and the energy derived from it in evaluation/energy.py) reflects
        # isolated execution — latency is measured inside architectures/base.py.
        architecture = self._build_arch(cfg, benchmark.task_type)

        # Console label
        if cfg.architecture == "monolithic":
            pair_label = f"(LLM only) {cfg.llm}"
        elif cfg.architecture in {"ensemble", "dynamic_bidding"} and (getattr(cfg, "ensemble_slms", None) or not cfg.slm):
            members = getattr(cfg, "ensemble_slms", None) or [cfg.slm or "?"]
            tiebreak = f" → tiebreak {cfg.llm}" if (cfg.architecture == "ensemble" and cfg.llm_tiebreak and cfg.llm) else ""
            prefix = "ensemble" if cfg.architecture == "ensemble" else "dynamic_bidding"
            pair_label = f"{prefix}[{', '.join(members)}]{tiebreak}"
        elif cfg.architecture in {"blackboard", "entropy_blackboard"}:
            pair_label = f"Swarm[{cfg.slm}, {cfg.secondary_slm}] → {cfg.llm}"
        elif cfg.architecture == "pure_swarm":
            pair_label = f"PureSwarm[{cfg.slm}, {cfg.secondary_slm}]"
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
            import dataclasses

            from mlops.tracking import MLflowTracker
            tracker = MLflowTracker(
                experiment_name=f"thesis-{cfg.architecture}",
                tracking_uri=cfg.mlflow_tracking_uri,
            )
            primary_id = cfg.llm if cfg.architecture == "monolithic" else (cfg.slm or cfg.llm or "model")
            tracker.start_run(
                run_name=f"{primary_id}-{cfg.benchmark}-{cfg.n_samples}",
                config=dataclasses.asdict(cfg),
            )
        except Exception:
            pass  # Suppressed MLFlow warnings to keep terminal clean

        # ------------------------------------------------------------------
        # Serial generate + off-critical-path post-processing.
        #
        # The main thread runs architecture.run(query) one query at a time —
        # this is the measured section, and latency_ms is sealed inside the
        # Response before it is handed off. A single background thread does
        # the rest: energy annotation, scoring (code benchmarks shell out to a
        # subprocess that can take seconds), MLflow logging and callbacks. That
        # bookkeeping now overlaps the next request instead of blocking it. The
        # GPU still only serves one request at a time, so the recorded metrics
        # are identical to the old fully-serial loop; only the wall-clock wait
        # between requests shrinks. The consumer is the sole writer of
        # result.samples, and it processes items in submit order (single
        # producer, single FIFO consumer), so ordering needs no extra work.
        # ------------------------------------------------------------------

        work_q: Queue = Queue()
        consumer_error: list[BaseException] = []
        sentinel = object()

        def consume() -> None:
            while True:
                item = work_q.get()
                if item is sentinel:
                    return
                query, response = item
                try:
                    response = annotate_response_resource_usage(response)
                    correct = benchmark.is_correct(response.predicted_answer, query)
                    sample_result = SampleResult(
                        query=query, response=response, correct=correct
                    )
                    result.samples.append(sample_result)
                    done = len(result.samples)

                    if tracker:
                        try:
                            tracker.log_sample(query.id, response.text, correct, response)
                        except Exception:
                            pass

                    if self.callbacks:
                        self.callbacks.sample_complete(done, len(queries), response, sample_result)
                        self.callbacks.metric_update("accuracy", result.n_correct / done)
                        self.callbacks.metric_update("llm_call_ratio", result.llm_call_ratio)

                    if done % 10 == 0 or done == len(queries):
                        print(
                            f"  [{done}/{len(queries)}] acc={result.accuracy:.3f} "
                            f"llm_ratio={result.llm_call_ratio:.3f} "
                            f"cost=${result.total_cost_usd:.4f} "
                            f"energy={result.total_energy_kwh:.4f}kWh"
                        )
                except BaseException as exc:  # noqa: BLE001 — surfaced to main thread
                    consumer_error.append(exc)
                    return

        consumer = threading.Thread(
            target=consume, name=f"{self.experiment_id}-consumer", daemon=True
        )
        consumer.start()

        cancelled = False
        gen_error: BaseException | None = None
        try:
            for query in queries:
                if self.callbacks and self.callbacks.is_cancelled():
                    cancelled = True
                    break
                if consumer_error:  # consumer died — stop feeding it
                    break
                response = architecture.run(query)
                work_q.put((query, response))
        except BaseException as exc:  # generate() failed
            gen_error = exc
        finally:
            work_q.put(sentinel)
            consumer.join()

        if cancelled:
            if tracker:
                tracker.end_run("KILLED")
            raise ExperimentCancelledError("Experiment cancelled by user.")

        failure = gen_error or (consumer_error[0] if consumer_error else None)
        if failure is not None:
            if self.callbacks:
                self.callbacks.error(failure)
            if tracker:
                tracker.end_run("FAILED")
            raise failure

        # Save reports
        baseline_metrics = self._resolve_recommended_baseline(cfg.benchmark, cfg.llm, n_samples=cfg.n_samples)
        reporter = Reporter(output_dir=cfg.output_dir)
        reporter.save(
            result,
            full_llm_cost_usd=baseline_metrics.get("total_cost_usd"),
            full_llm_avg_algorithmic_latency_ms=baseline_metrics.get("avg_algorithmic_latency_ms"),
            full_llm_energy_kwh=baseline_metrics.get("total_energy_kwh"),
        )
        final_metrics = compute_metrics(
            result,
            full_llm_cost_usd=baseline_metrics.get("total_cost_usd"),
            full_llm_avg_algorithmic_latency_ms=baseline_metrics.get("avg_algorithmic_latency_ms"),
            full_llm_energy_kwh=baseline_metrics.get("total_energy_kwh"),
        )

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

    @staticmethod
    def _resolve_recommended_baseline(benchmark: str, llm: str | None = None, n_samples: int | None = None) -> dict[str, float]:
        return resolve_recommended_baseline(benchmark, llm, n_samples=n_samples)

    def multi_run(
        self,
        n_runs: int = 3,
        seeds: list[int] | None = None,
    ) -> dict:
        """Run the same config N times with different seeds and aggregate results.

        Returns a dict with:
          - ``runs``: list of ExperimentResult (one per run)
          - ``aggregated``: mean ± std metrics dict from aggregate_runs()

        Seeds default to [42, 43, 44, ...] when not provided. Per CLAUDE.md §9,
        minimum n_runs=3 is required for thesis-grade reporting.
        """
        if seeds is None:
            seeds = list(range(42, 42 + n_runs))
        if len(seeds) < n_runs:
            raise ValueError(f"Need {n_runs} seeds, got {len(seeds)}")

        import dataclasses

        baseline_metrics = self._resolve_recommended_baseline(self.config.benchmark, self.config.llm, n_samples=self.config.n_samples)
        all_results: list[ExperimentResult] = []
        all_metrics: list[dict] = []

        for i, seed in enumerate(seeds[:n_runs]):
            cfg = dataclasses.replace(self.config, seed=seed)
            runner = ExperimentRunner(cfg, callbacks=self.callbacks)
            result = runner.run()
            all_results.append(result)
            m = compute_metrics(
                result,
                full_llm_cost_usd=baseline_metrics.get("total_cost_usd"),
                full_llm_avg_algorithmic_latency_ms=baseline_metrics.get("avg_algorithmic_latency_ms"),
                full_llm_energy_kwh=baseline_metrics.get("total_energy_kwh"),
            )
            all_metrics.append(m)
            print(f"  [run {i + 1}/{n_runs}] seed={seed} acc={m.get('accuracy', 0):.3f}")

        aggregated = aggregate_runs(all_metrics)

        reporter = Reporter(output_dir=self.config.output_dir)
        reporter.save_multi_run(
            config=self.config,
            runs=all_results,
            aggregated=aggregated,
        )

        return {"runs": all_results, "aggregated": aggregated}

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
