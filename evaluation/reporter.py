"""Generates JSON + Markdown reports from experiment results."""
from __future__ import annotations

import dataclasses
import json
from datetime import datetime, timezone
from pathlib import Path

from core.types import ExperimentResult
from evaluation.metrics import compute_metrics


class Reporter:
    def __init__(self, output_dir: str | Path = "results") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        result: ExperimentResult,
        full_llm_cost_usd: float | None = None,
    ) -> Path:
        metrics = compute_metrics(result, full_llm_cost_usd)
        now = datetime.now(timezone.utc).isoformat()

        report = {
            "experiment_id": result.experiment_id,
            "created_at": now,
            "config": dataclasses.asdict(result.config),
            "metrics": metrics,
            "samples": [
                self._sample_payload(s)
                for s in result.samples
            ],
        }

        json_path = self.output_dir / f"{result.experiment_id}.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        md_path = self.output_dir / f"{result.experiment_id}.md"
        self._write_markdown(md_path, report, metrics, result)

        return json_path

    def _write_markdown(
        self,
        path: Path,
        report: dict,
        metrics: dict,
        result: ExperimentResult,
    ) -> None:
        cfg = result.config
        lines = [
            f"# Experiment Report — {result.experiment_id}",
            f"**Date:** {report['created_at']}  ",
            "",
            "## Configuration",
            f"| Parameter | Value |",
            f"|-----------|-------|",
            f"| Architecture | {cfg.architecture} |",
            f"| Benchmark | {cfg.benchmark} |",
            f"| SLM | {cfg.slm} |",
            f"| LLM | {cfg.llm} |",
            f"| N Samples | {cfg.n_samples} |",
            f"| Confidence Threshold | {cfg.confidence_threshold} |",
            "",
            "## Results",
            "| Metric | Value |",
            "|--------|-------|",
        ]
        for k, v in metrics.items():
            if isinstance(v, float):
                lines.append(f"| {k} | {v:.4f} |")
            else:
                lines.append(f"| {k} | {v} |")

        lines += [
            "",
            "## EATS Score Interpretation",
            f"**EATS = {metrics.get('eats_score', 0):.4f}**  ",
            f"Accuracy: {metrics.get('accuracy', 0):.2%}  ",
            f"LLM Call Ratio: {metrics.get('llm_call_ratio', 0):.2%}  ",
            f"Total Cost: ${metrics.get('total_cost_usd', 0):.4f}  ",
        ]

        with open(path, "w") as f:
            f.write("\n".join(lines))

    @staticmethod
    def _sample_payload(sample) -> dict:
        metadata = sample.response.metadata
        escalated = bool(metadata.get("escalated", sample.response.llm_calls))
        payload = {
            "query_id": sample.query.id,
            "query_text": sample.query.text,
            "correct": sample.correct,
            "predicted": sample.response.predicted_answer,
            "ground_truth": sample.query.answer,
            "llm_calls": sample.response.llm_calls,
            "confidence": sample.response.confidence,
            "latency_ms": sample.response.latency_ms,
            "cost_usd": sample.response.cost_usd,
            "final_model_id": metadata.get("final_model_id", sample.response.model_id),
            "used_llm": escalated,
            "escalated": escalated,
            "slm_confidence": metadata.get("slm_confidence", sample.response.confidence),
            "confidence_threshold": metadata.get("confidence_threshold"),
            "slm_latency_ms": metadata.get("slm_latency_ms"),
            "llm_latency_ms": metadata.get("llm_latency_ms"),
            "slm_input_tokens": metadata.get("slm_input_tokens"),
            "slm_output_tokens": metadata.get("slm_output_tokens"),
            "llm_input_tokens": metadata.get("llm_input_tokens"),
            "llm_output_tokens": metadata.get("llm_output_tokens"),
            "slm_cost_usd": metadata.get("slm_cost_usd"),
            "llm_cost_usd": metadata.get("llm_cost_usd"),
        }
        if escalated:
            payload.update(
                {
                    "prompt_text": metadata.get("prompt_text"),
                    "slm_text": metadata.get("slm_text"),
                    "final_text": sample.response.text,
                }
            )
        return payload
