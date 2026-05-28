"""Host topology and lock-status endpoints.

`GET /api/hosts` returns the catalog of physical hosts together with the
model currently being served on each (probed live via /v1/models) and the
process-wide reservation lock status.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from core.hosts import list_hosts
from web.backend.dependencies import Settings, get_settings
from web.backend.schemas import HostsResponse, HostStatus
from web.backend.services.model_host_service import probe_host

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("", response_model=HostsResponse)
def list_host_status(settings: Settings = Depends(get_settings)) -> HostsResponse:
    hosts: list[HostStatus] = []
    for host in list_hosts():
        snapshot = probe_host(host)
        hosts.append(HostStatus(**snapshot))
    return HostsResponse(
        hosts=hosts,
        autoswitch_enabled=bool(getattr(settings, "rtx6000_autoswitch_enabled", False)),
    )
