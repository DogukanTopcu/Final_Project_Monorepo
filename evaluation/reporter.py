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
        config_payload = dataclasses.asdict(result.config)
        if result.config.architecture == "routing":
            config_payload["routing_policy"] = {
                "confidence_threshold": result.config.confidence_threshold,
                "margin_threshold": result.config.margin_threshold,
                "long_input_token_threshold": result.config.long_input_token_threshold,
                "parse_failure_escalates": True,
                "force_escalate": result.config.force_escalate,
            }

        report = {
            "experiment_id": result.experiment_id,
            "created_at": now,
            "config": config_payload,
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
            f"| SLM Temperature | {cfg.slm_temperature} |",
            f"| LLM Temperature | {cfg.llm_temperature} |",
            f"| SLM Max Tokens | {cfg.slm_max_tokens} |",
            f"| LLM Max Tokens | {cfg.llm_max_tokens} |",
            f"| SLM Only | {cfg.slm_only} |",
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
            f"Normalized Efficiency Penalty: {metrics.get('normalized_efficiency_penalty', 0):.4f}  ",
            f"Total Cost: ${metrics.get('total_cost_usd', 0):.4f}  ",
        ]

        with open(path, "w") as f:
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
