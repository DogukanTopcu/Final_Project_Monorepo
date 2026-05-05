from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from web.backend.schemas import (
    ExperimentCreate,
    ExperimentLaunchResponse,
    ExperimentResponse,
    ExperimentStatus,
)
from web.backend.services import experiment_service

router = APIRouter(tags=["experiments"])


@router.post("/experiments", response_model=ExperimentLaunchResponse)
async def launch_experiment(params: ExperimentCreate):
    exp = experiment_service.launch_experiment(params)
    return ExperimentLaunchResponse(
        experiment_id=exp.experiment_id,
        status=exp.status,
    )


@router.get("/experiments", response_model=list[ExperimentResponse])
async def list_experiments():
    return experiment_service.list_experiments()


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str):
    exp = experiment_service.get_experiment(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.delete("/experiments/{experiment_id}")
async def cancel_experiment(experiment_id: str):
    if not experiment_service.cancel_experiment(experiment_id):
        raise HTTPException(status_code=404, detail="Experiment not found")
    return {"status": "cancelled", "experiment_id": experiment_id}


@router.get("/experiments/{experiment_id}/stream")
async def stream_experiment(experiment_id: str):
    exp = experiment_service.get_experiment(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        last_idx = 0
        heartbeat_counter = 0

        while True:
            events = experiment_service.get_events(experiment_id)
            new_events = events[last_idx:]
            last_idx = len(events)

            for event in new_events:
                yield f"data: {json.dumps(event)}\n\n"

            current = experiment_service.get_experiment(experiment_id)
            if current and current.status in (
                ExperimentStatus.COMPLETED,
                ExperimentStatus.FAILED,
                ExperimentStatus.CANCELLED,
            ):
                if not new_events:
                    yield f"data: {json.dumps({'type': 'complete', 'experiment_id': experiment_id, 'status': current.status.value})}\n\n"
                break

            heartbeat_counter += 1
            if heartbeat_counter % 15 == 0:
                yield ": heartbeat\n\n"

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
