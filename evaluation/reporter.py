"""Generates JSON + Markdown reports from experiment results."""
from __future__ import annotations

import dataclasses
import json
from datetime import UTC, datetime
from pathlib import Path

from core.types import ExperimentConfig, ExperimentResult
from evaluation.metrics import compute_metrics, compute_subject_accuracy


class Reporter:
    def __init__(self, output_dir: str | Path = "results") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        result: ExperimentResult,
        full_llm_cost_usd: float | None = None,
        full_llm_avg_algorithmic_latency_ms: float | None = None,
        full_llm_energy_kwh: float | None = None,
    ) -> Path:
        metrics = compute_metrics(
            result,
            full_llm_cost_usd=full_llm_cost_usd,
            full_llm_avg_algorithmic_latency_ms=full_llm_avg_algorithmic_latency_ms,
            full_llm_energy_kwh=full_llm_energy_kwh,
        )
        now = datetime.now(UTC).isoformat()
        config_payload = dataclasses.asdict(result.config)
        if result.config.architecture == "routing":
            config_payload["routing_policy"] = {
                "confidence_threshold": result.config.confidence_threshold,
                "margin_threshold": result.config.margin_threshold,
                "long_input_token_threshold": result.config.long_input_token_threshold,
                "parse_failure_escalates": True,
                "force_escalate": result.config.force_escalate,
            }

        subject_accuracy = compute_subject_accuracy(result)

        report = {
            "experiment_id": result.experiment_id,
            "created_at": now,
            "completed_at": now,
            "config": config_payload,
            "metrics": metrics,
            "subject_accuracy": subject_accuracy,
            "samples": [
                self._sample_payload(s)
                for s in result.samples
            ],
        }

        json_path = self.output_dir / f"{result.experiment_id}.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        md_path = self.output_dir / f"{result.experiment_id}.md"
        self._write_markdown(md_path, report, metrics, result, subject_accuracy)

        return json_path

    def save_multi_run(
        self,
        config: ExperimentConfig,
        runs: list[ExperimentResult],
        aggregated: dict,
    ) -> Path:
        """Save a mean ± std summary report for N repeated runs of the same config."""
        import dataclasses

        now = datetime.now(UTC).isoformat()
        run_id = f"multi_{config.architecture}_{config.benchmark}_{len(runs)}runs"

        report = {
            "run_id": run_id,
            "created_at": now,
            "n_runs": len(runs),
            "config": dataclasses.asdict(config),
            "aggregated": aggregated,
            "run_ids": [r.experiment_id for r in runs],
        }

        json_path = self.output_dir / f"{run_id}.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        md_path = self.output_dir / f"{run_id}.md"
        _KEY_LABELS = {
            "accuracy": "Accuracy",
            "latency_p95_ms": "Latency p95 (ms)",
            "throughput_tokens_per_sec": "Throughput (tok/s)",
            "cost_per_query_usd": "Cost/query ($)",
            "normalized_cost": "Cost vs baseline",
            "joules_per_output_token": "J/output token",
            "total_co2_g": "CO₂ (g)",
            "eats_score": "EATS",
            "escalation_rate": "Escalation rate",
            "ece": "ECE",
        }
        lines = [
            f"# Multi-Run Report — {run_id}",
            f"**Date:** {now}  ",
            f"**Runs:** {len(runs)} (seeds: {[r.config.seed for r in runs]})  ",
            "",
            "## Configuration",
            f"| Architecture | {config.architecture} |",
            "|---|---|",
            f"| Benchmark | {config.benchmark} |",
            f"| SLM | {config.slm or '—'} |",
            f"| LLM | {config.llm or '—'} |",
            f"| N samples/run | {config.n_samples} |",
            "",
            "## Aggregated Results (mean ± std)",
            "| Metric | Mean | Std |",
            "|--------|------|-----|",
        ]
        for key, label in _KEY_LABELS.items():
            mean = aggregated.get(f"{key}_mean")
            std = aggregated.get(f"{key}_std")
            if mean is None:
                continue
            if key in ("accuracy", "escalation_rate", "ece", "normalized_cost"):
                lines.append(f"| {label} | {mean:.4f} | ±{std:.4f} |")
            elif key in ("latency_p95_ms", "throughput_tokens_per_sec"):
                lines.append(f"| {label} | {mean:.1f} | ±{std:.1f} |")
            else:
                lines.append(f"| {label} | {mean:.6f} | ±{std:.6f} |")

        lines += [
            "",
            "## Individual Run IDs",
        ]
        for r in runs:
            lines.append(f"- `{r.experiment_id}` (seed={r.config.seed})")

        with open(md_path, "w") as f:
            f.write("\n".join(lines))

        return json_path

    def _write_markdown(
        self,
        path: Path,
        report: dict,
        metrics: dict,
        result: ExperimentResult,
        subject_accuracy: dict | None = None,
    ) -> None:
        cfg = result.config
        acc = metrics.get("accuracy", 0.0)
        ci_low = metrics.get("accuracy_ci_low_95", 0.0)
        ci_high = metrics.get("accuracy_ci_high_95", 0.0)

        lines = [
            f"# Experiment Report — {result.experiment_id}",
            f"**Date:** {report['created_at']}  ",
            "",
            "## Configuration",
            "| Parameter | Value |",
            "|-----------|-------|",
            f"| Architecture | {cfg.architecture} |",
            f"| Benchmark | {cfg.benchmark} |",
            f"| SLM | {cfg.slm} |",
            f"| LLM | {cfg.llm} |",
            f"| SLM Temperature | {cfg.slm_temperature} |",
            f"| LLM Temperature | {cfg.llm_temperature} |",
            f"| SLM Max Tokens | {cfg.slm_max_tokens} |",
            f"| LLM Max Tokens | {cfg.llm_max_tokens} |",
            f"| SLM Only | {cfg.slm_only} |",
            f"| N Samples | {cfg.n_samples} |",
            f"| Confidence Threshold | {cfg.confidence_threshold} |",
            "",
            "## Accuracy",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Accuracy | {acc:.2%} |",
            f"| 95% CI | [{ci_low:.2%}, {ci_high:.2%}] |",
            f"| Correct / Total | {int(metrics.get('n_correct', 0))} / {int(metrics.get('n_total', 0))} |",
            f"| Escalation Rate | {metrics.get('escalation_rate', 0.0):.2%} |",
            f"| ECE (confidence calibration) | {metrics.get('ece', 0.0):.4f} |",
            "",
            "## Latency",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Throughput (output tok/s) | {metrics.get('throughput_tokens_per_sec', 0.0):.1f} |",
            f"| Wall-clock avg (ms) | {metrics.get('avg_latency_ms', 0.0):.1f} |",
            f"| Algorithmic avg (ms) | {metrics.get('avg_algorithmic_latency_ms', 0.0):.1f} |",
            f"| Wall-clock p50 (ms) | {metrics.get('latency_p50_ms', 0.0):.1f} |",
            f"| Wall-clock p95 (ms) | {metrics.get('latency_p95_ms', 0.0):.1f} |",
            "",
            "> **Wall-clock**: observed end-to-end time including network and queue.  ",
            "> **Algorithmic**: intrinsic inference + orchestration time summed across steps.",
            "",
            "## Cost",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Cost per query (USD) | ${metrics.get('cost_per_query_usd', 0.0):.6f} |",
            f"| Total cost (USD) | ${metrics.get('total_cost_usd', 0.0):.4f} |",
            f"| API cost (USD) | ${metrics.get('total_api_cost_usd', 0.0):.4f} |",
            f"| Infra cost (USD) | ${metrics.get('total_infra_cost_usd', 0.0):.4f} |",
            f"| SLM API cost — all queries (USD) | ${metrics.get('total_slm_api_cost_usd', 0.0):.4f} |",
            f"| LLM API cost — escalated only (USD) | ${metrics.get('total_llm_api_cost_usd', 0.0):.4f} |",
            f"| SLM-path total (non-escalated queries) | ${metrics.get('cost_slm_path_usd', 0.0):.4f} |",
            f"| Escalated-path total (SLM+LLM) | ${metrics.get('cost_escalated_path_usd', 0.0):.4f} |",
            f"| SLM-path cost fraction | {metrics.get('cost_slm_path_fraction', 0.0):.2%} |",
            f"| Normalized cost (vs baseline) | {metrics.get('normalized_cost', 1.0):.4f} |",
            "",
            "## Energy",
            "| Metric | Value |",
            "|--------|-------|",
            f"| **Joules per output token** | {metrics.get('joules_per_output_token', 0.0):.6f} J/tok |",
            f"| Total energy (kWh) | {metrics.get('total_energy_kwh', 0.0):.6f} |",
            f"| Avg energy per sample (kWh) | {metrics.get('avg_energy_per_sample_kwh', 0.0):.8f} |",
            f"| Total CO₂ (g) | {metrics.get('total_co2_g', 0.0):.4f} |",
            f"| Avg CO₂ per sample (g) | {metrics.get('avg_co2_per_sample_g', 0.0):.6f} |",
            f"| Normalized energy (vs baseline) | {metrics.get('normalized_energy', 1.0):.4f} |",
            "",
            "## EATS Score",
            f"**EATS = {metrics.get('eats_score', 0):.4f}**  ",
            f"Normalized efficiency penalty: {metrics.get('normalized_efficiency_penalty', 0):.4f}  ",
            "",
            "> EATS = accuracy² / (accuracy² + cost^0.5 × latency^0.3 × energy^0.2).  ",
            "> Range [0, 1]; higher is better. Penalties are relative to the monolithic LLM baseline.",
        ]

        arch = cfg.architecture
        breakdown: list[str] = []
        if arch == "routing":
            breakdown = [
                "",
                "## Routing Breakdown",
                "| Path | Accuracy | N queries |",
                "|------|----------|-----------|",
                f"| SLM-handled (no escalation) | {metrics.get('accuracy_slm_handled', 0.0):.2%} | {int(metrics.get('n_slm_only', 0))} |",
                f"| LLM-handled (escalated) | {metrics.get('accuracy_llm_handled', 0.0):.2%} | {int(metrics.get('n_escalated', 0))} |",
                f"| Escalation rate | {metrics.get('escalation_rate', 0.0):.2%} | — |",
            ]
        elif arch == "ensemble":
            breakdown = [
                "",
                "## Ensemble Breakdown",
                "| Path | Accuracy | N queries |",
                "|------|----------|-----------|",
                f"| Majority vote (no tiebreak) | {metrics.get('accuracy_majority_vote', 0.0):.2%} | {int(metrics.get('n_slm_only', 0))} |",
                f"| LLM tiebreak | {metrics.get('accuracy_llm_handled', 0.0):.2%} | {int(metrics.get('n_escalated', 0))} |",
                f"| Tiebreak rate | {metrics.get('llm_tiebreak_rate', 0.0):.2%} | — |",
            ]
        elif arch == "active_oracle":
            breakdown = [
                "",
                "## Active Oracle Breakdown",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Oracle query rate | {metrics.get('oracle_query_rate', 0.0):.2%} |",
                f"| LLM calls total | {int(metrics.get('n_escalated', 0))} |",
            ]
        elif arch == "multi_agent":
            breakdown = [
                "",
                "## Multi-Agent Breakdown",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Arbitrator | {cfg.arbitrator} |",
                f"| LLM arbitration rate | {metrics.get('escalation_rate', 0.0):.2%} |",
            ]

        lines += breakdown

        if subject_accuracy:
            for field, acc_map in subject_accuracy.items():
                label = "Subject" if field == "subject" else "Difficulty"
                lines += [
                    "",
                    f"## Accuracy by {label}",
                    f"| {label} | Accuracy | N |",
                    "|---|---|---|",
                ]
                for group, acc in acc_map.items():
                    n = sum(
                        1 for s in result.samples
                        if s.query.metadata.get(field) == group
                    )
                    lines.append(f"| {group} | {acc:.2%} | {n} |")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def _sample_payload(sample) -> dict:
        metadata = sample.response.metadata
        algorithmic_latency_ms = Reporter._algorithmic_latency_of(sample.response)
        escalated = bool(metadata.get("escalated", sample.response.llm_calls))
        slm_raw_text = metadata.get("slm_raw_text", metadata.get("slm_text"))
        slm_parsed_answer = metadata.get("slm_parsed_answer")
        llm_raw_text = metadata.get("llm_raw_text", metadata.get("llm_text"))
        llm_parsed_answer = metadata.get("llm_parsed_answer")
        final_raw_text = metadata.get("final_raw_text", sample.response.text)
        final_parsed_answer = metadata.get(
            "final_parsed_answer",
            sample.response.predicted_answer,
        )
        slm_parse_status = metadata.get("slm_parse_status")
        if slm_parse_status is None:
            slm_parse_status = "parsed" if slm_parsed_answer is not None else "unparseable"
        llm_parse_status = metadata.get("llm_parse_status")
        final_answer_source = metadata.get(
            "final_answer_source",
            "llm" if escalated else "slm",
        )
        routing_decision = metadata.get("routing_decision") or {
            "accepted_by": "llm" if escalated else "slm",
            "threshold": metadata.get("confidence_threshold"),
            "confidence_method": metadata.get("confidence_method"),
            "signals": {
                "parse_success": slm_parsed_answer is not None,
                "confidence": metadata.get("slm_confidence", sample.response.confidence),
                "top2_margin": metadata.get("top2_margin"),
                "input_tokens": metadata.get("slm_input_tokens", sample.response.input_tokens),
                "input_too_long": False,
                "low_confidence": False,
                "low_margin": False,
                "forced_escalation": bool(metadata.get("force_escalate", False)),
            },
        }
        payload = {
            "query_id": sample.query.id,
            "query_text": sample.query.text,
            "query_choices": sample.query.choices,
            "correct": sample.correct,
            "predicted": final_parsed_answer,
            "ground_truth": sample.query.answer,
            "llm_calls": sample.response.llm_calls,
            "confidence": sample.response.confidence,
            "latency_ms": sample.response.latency_ms,
            "algorithmic_latency_ms": algorithmic_latency_ms,
            "cost_usd": sample.response.cost_usd,
            "api_cost_usd": sample.response.api_cost_usd,
            "infra_cost_usd": sample.response.infra_cost_usd,
            "energy_kwh": sample.response.energy_kwh,
            "co2_g": sample.response.co2_g,
            "gpu_power_w": sample.response.gpu_power_w,
            "final_model_id": metadata.get("final_model_id", sample.response.model_id),
            "used_llm": escalated,
            "escalated": escalated,
            "slm_confidence": metadata.get("slm_confidence", sample.response.confidence),
            "confidence_threshold": metadata.get("confidence_threshold"),
            "margin_threshold": metadata.get("margin_threshold"),
            "long_input_token_threshold": metadata.get("long_input_token_threshold"),
            "confidence_method": metadata.get("confidence_method"),
            "slm_raw_text": slm_raw_text,
            "slm_parsed_answer": slm_parsed_answer,
            "slm_parse_status": slm_parse_status,
            "llm_raw_text": llm_raw_text,
            "llm_parsed_answer": llm_parsed_answer,
            "llm_parse_status": llm_parse_status,
            "final_raw_text": final_raw_text,
            "final_parsed_answer": final_parsed_answer,
            "final_answer_source": final_answer_source,
            "escalation_reason": metadata.get("escalation_reason"),
            "routing_decision": routing_decision,
            "slm_latency_ms": metadata.get("slm_latency_ms"),
            "llm_latency_ms": metadata.get("llm_latency_ms"),
            "slm_input_tokens": metadata.get("slm_input_tokens"),
            "slm_output_tokens": metadata.get("slm_output_tokens"),
            "llm_input_tokens": metadata.get("llm_input_tokens"),
            "llm_output_tokens": metadata.get("llm_output_tokens"),
            "slm_cost_usd": metadata.get("slm_cost_usd"),
            "llm_cost_usd": metadata.get("llm_cost_usd"),
            "resource_estimate": metadata.get("resource_estimate"),
            "inference_steps": metadata.get("inference_steps", []),
            "prompt_text": metadata.get("prompt_text"),
            "slm_text": slm_raw_text,
            "final_text": final_raw_text,
        }
        for key, value in metadata.items():
            payload.setdefault(key, value)
        return payload

    @staticmethod
    def _algorithmic_latency_of(response) -> float:
        if response.algorithmic_latency_ms > 0:
            return response.algorithmic_latency_ms
        metadata_latency = response.metadata.get("algorithmic_latency_ms")
        if isinstance(metadata_latency, (int, float)) and metadata_latency > 0:
            return float(metadata_latency)
        steps = response.metadata.get("inference_steps")
        if isinstance(steps, list):
            total = 0.0
            found = False
            for step in steps:
                if isinstance(step, dict):
                    latency = step.get("latency_ms")
                    if isinstance(latency, (int, float)):
                        total += float(latency)
                        found = True
            if found:
                return total
        return response.latency_ms
