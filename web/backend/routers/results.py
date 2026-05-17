from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ComparisonResponse, ResultDetail, ResultSummary
from web.backend.services import aws_service, experiment_service

router = APIRouter(tags=["results"])


def _load_in_memory_results() -> dict[str, ResultSummary]:
    result_map: dict[str, ResultSummary] = {}
    for exp in experiment_service.list_experiments():
        if exp.metrics is None:
            continue
        result_map[exp.experiment_id] = ResultSummary(
            id=exp.experiment_id,
            experiment_id=exp.experiment_id,
            architecture=exp.architecture.value,
            benchmark=exp.benchmark.value,
            slm=exp.slm,
            llm=exp.llm,
            accuracy=exp.metrics.get("accuracy", 0.0),
            avg_latency_ms=exp.metrics.get("avg_latency_ms"),
            eats_score=exp.metrics.get("eats_score"),
            llm_call_ratio=exp.metrics.get("llm_call_ratio"),
            total_cost_usd=exp.metrics.get("total_cost_usd"),
            created_at=exp.created_at,
        )
    return result_map


def _load_local_result_summaries(settings: Settings) -> dict[str, ResultSummary]:
    result_map: dict[str, ResultSummary] = {}
    results_dir = Path(settings.results_dir)
    if not results_dir.exists():
        return result_map

    for path in sorted(results_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue

        config = data.get("config", {})
        metrics = data.get("metrics", {})
        experiment_id = data.get("experiment_id", path.stem)
        result_map[experiment_id] = ResultSummary(
            id=experiment_id,
            experiment_id=experiment_id,
            architecture=config.get("architecture", "unknown"),
            benchmark=config.get("benchmark", "unknown"),
            slm=config.get("slm", "unknown"),
            llm=config.get("llm", "unknown"),
            accuracy=metrics.get("accuracy", 0.0),
            avg_latency_ms=metrics.get("avg_latency_ms"),
            eats_score=metrics.get("eats_score"),
            llm_call_ratio=metrics.get("llm_call_ratio"),
            total_cost_usd=metrics.get("total_cost_usd"),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
        )
    return result_map


def _load_s3_result_summaries(settings: Settings) -> dict[str, ResultSummary]:
    result_map: dict[str, ResultSummary] = {}
    for file_info in aws_service.list_s3_results(settings.s3_results_bucket):
        try:
            data = json.loads(
                aws_service.get_s3_object(settings.s3_results_bucket, file_info["key"])
            )
        except Exception:
            continue

        config = data.get("config", {})
        metrics = data.get("metrics", {})
        experiment_id = data.get("experiment_id", Path(file_info["key"]).stem)
        result_map[experiment_id] = ResultSummary(
            id=experiment_id,
            experiment_id=experiment_id,
            architecture=config.get("architecture", "unknown"),
            benchmark=config.get("benchmark", "unknown"),
            slm=config.get("slm", "unknown"),
            llm=config.get("llm", "unknown"),
            accuracy=metrics.get("accuracy", 0.0),
            avg_latency_ms=metrics.get("avg_latency_ms"),
            eats_score=metrics.get("eats_score"),
            llm_call_ratio=metrics.get("llm_call_ratio"),
            total_cost_usd=metrics.get("total_cost_usd"),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
        )
    return result_map


def _collect_result_summaries(settings: Settings) -> dict[str, ResultSummary]:
    results = _load_in_memory_results()
    results.update(_load_local_result_summaries(settings))
    results.update(_load_s3_result_summaries(settings))
    return results


@router.get("/results", response_model=list[ResultSummary])
async def list_results(settings: Settings = Depends(get_settings)):
    results = _collect_result_summaries(settings)
    return sorted(
        results.values(),
        key=lambda result: result.created_at,
        reverse=True,
    )


@router.get("/results/compare", response_model=ComparisonResponse)
async def compare_results(
    ids: str = Query(..., description="Comma-separated IDs"),
    settings: Settings = Depends(get_settings),
):
    id_list = [item.strip() for item in ids.split(",") if item.strip()]
    if len(id_list) < 2 or len(id_list) > 4:
        raise HTTPException(
            status_code=400,
            detail="Provide 2-4 experiment IDs to compare",
        )

    results = _collect_result_summaries(settings)
    metrics: dict[str, dict[str, float]] = {}
    for result_id in id_list:
        result = results.get(result_id)
        if result is None:
            metrics[result_id] = {}
            continue
        metrics[result_id] = {
            key: value
            for key, value in {
                "accuracy": result.accuracy,
                "avg_latency_ms": result.avg_latency_ms,
                "eats_score": result.eats_score,
                "llm_call_ratio": result.llm_call_ratio,
                "total_cost_usd": result.total_cost_usd,
            }.items()
            if value is not None
        }

    return ComparisonResponse(ids=id_list, metrics=metrics)


@router.get("/results/{result_id}", response_model=ResultDetail)
async def get_result(result_id: str, settings: Settings = Depends(get_settings)):
    local_path = Path(settings.results_dir) / f"{result_id}.json"
    if local_path.exists():
        try:
            data = json.loads(local_path.read_text())
            return ResultDetail(
                id=result_id,
                experiment_id=data.get("experiment_id", result_id),
                architecture=data.get("config", {}).get("architecture", "unknown"),
                benchmark=data.get("config", {}).get("benchmark", "unknown"),
                metrics=data.get("metrics", {}),
                samples=data.get("samples", []),
                config=data.get("config", {}),
                created_at=datetime.fromisoformat(
                    data.get("created_at", datetime.now(timezone.utc).isoformat())
                ),
            )
        except Exception:
            pass

    exp = experiment_service.get_experiment(result_id)
    if exp and exp.metrics:
        return ResultDetail(
            id=result_id,
            experiment_id=exp.experiment_id,
            architecture=exp.architecture.value,
            benchmark=exp.benchmark.value,
            metrics=exp.metrics,
            config=exp.config_overrides,
            created_at=exp.created_at,
        )

    try:
        data = json.loads(
            aws_service.get_s3_object(settings.s3_results_bucket, result_id)
        )
        return ResultDetail(
            id=result_id,
            experiment_id=data.get("experiment_id", result_id),
            architecture=data.get("config", {}).get("architecture", "unknown"),
            benchmark=data.get("config", {}).get("benchmark", "unknown"),
            metrics=data.get("metrics", {}),
            samples=data.get("samples", []),
            config=data.get("config", {}),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail="Result not found") from exc
