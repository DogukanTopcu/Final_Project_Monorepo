from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import ComparisonResponse, ResultDetail, ResultSummary
from web.backend.services import experiment_service, gcp_service

router = APIRouter(tags=["results"])


@router.get("/results", response_model=list[ResultSummary])
async def list_results(settings: Settings = Depends(get_settings)):
    experiments = experiment_service.list_experiments()
    results: list[ResultSummary] = []
    for exp in experiments:
        if exp.metrics is None:
            continue
        results.append(
            ResultSummary(
                id=exp.experiment_id,
                experiment_id=exp.experiment_id,
                architecture=exp.architecture.value,
                benchmark=exp.benchmark.value,
                slm=exp.slm,
                llm=exp.llm,
                accuracy=exp.metrics.get("accuracy", 0.0),
                eats_score=exp.metrics.get("eats_score"),
                llm_call_ratio=exp.metrics.get("llm_call_ratio"),
                total_cost=exp.metrics.get("total_cost"),
                created_at=exp.created_at,
            )
        )

    gcs_files = gcp_service.list_gcs_results(settings.gcs_results_bucket)
    for f in gcs_files:
        try:
            data = json.loads(
                gcp_service.get_gcs_object(settings.gcs_results_bucket, f["key"])
            )
            results.append(
                ResultSummary(
                    id=f["key"],
                    experiment_id=data.get("experiment_id", f["key"]),
                    architecture=data.get("architecture", "unknown"),
                    benchmark=data.get("benchmark", "unknown"),
                    slm=data.get("slm", "unknown"),
                    llm=data.get("llm", "unknown"),
                    accuracy=data.get("accuracy", 0.0),
                    eats_score=data.get("eats_score"),
                    llm_call_ratio=data.get("llm_call_ratio"),
                    total_cost=data.get("total_cost"),
                    created_at=datetime.fromisoformat(
                        data.get("created_at", datetime.now(timezone.utc).isoformat())
                    ),
                )
            )
        except Exception:
            continue

    return results


@router.get("/results/compare", response_model=ComparisonResponse)
async def compare_results(ids: str = Query(..., description="Comma-separated IDs")):
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if len(id_list) < 2 or len(id_list) > 4:
        raise HTTPException(
            status_code=400, detail="Provide 2-4 experiment IDs to compare"
        )

    metrics: dict[str, dict[str, float]] = {}
    for eid in id_list:
        exp = experiment_service.get_experiment(eid)
        if exp and exp.metrics:
            metrics[eid] = exp.metrics
        else:
            metrics[eid] = {}

    return ComparisonResponse(ids=id_list, metrics=metrics)


@router.get("/results/{result_id}", response_model=ResultDetail)
async def get_result(result_id: str, settings: Settings = Depends(get_settings)):
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
            gcp_service.get_gcs_object(settings.gcs_results_bucket, result_id)
        )
        return ResultDetail(
            id=result_id,
            experiment_id=data.get("experiment_id", result_id),
            architecture=data.get("architecture", "unknown"),
            benchmark=data.get("benchmark", "unknown"),
            metrics=data.get("metrics", {}),
            samples=data.get("samples", []),
            config=data.get("config", {}),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now(timezone.utc).isoformat())
            ),
        )
    except Exception:
        raise HTTPException(status_code=404, detail="Result not found")
