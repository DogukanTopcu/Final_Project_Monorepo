from __future__ import annotations

from fastapi import APIRouter, HTTPException

from web.backend.schemas import CostEstimate, InstanceInfo
from web.backend.services import aws_service

router = APIRouter(tags=["infrastructure"])


@router.get("/infrastructure/instances", response_model=list[InstanceInfo])
async def list_instances():
    try:
        return aws_service.list_instances()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AWS error: {e}")


@router.post("/infrastructure/instances/{instance_id}/start")
async def start_instance(instance_id: str):
    try:
        result = aws_service.start_instance(instance_id)
        return {"instance_id": instance_id, "state": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AWS error: {e}")


@router.post("/infrastructure/instances/{instance_id}/stop")
async def stop_instance(instance_id: str):
    try:
        result = aws_service.stop_instance(instance_id)
        return {"instance_id": instance_id, "state": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AWS error: {e}")


@router.get("/infrastructure/costs", response_model=CostEstimate)
async def get_costs():
    try:
        return aws_service.get_cost_estimate()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AWS error: {e}")
