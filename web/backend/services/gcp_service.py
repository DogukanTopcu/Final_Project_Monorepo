from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1

from web.backend.dependencies import (
    get_bigquery_client,
    get_instances_client,
    get_settings,
    get_storage_client,
)
from web.backend.schemas import CostEstimate, InstanceInfo


def _wait_for_operation(operation: ExtendedOperation) -> None:
    operation.result(timeout=300)
    if operation.error_code:
        raise RuntimeError(operation.error_message or "GCP operation failed")


def _parse_instance_ref(instance_ref: str) -> tuple[str, str]:
    parts = instance_ref.split(":", 1)
    if len(parts) != 2:
        raise ValueError(
            "instance_id must be in 'zone:instance-name' format for GCP operations"
        )
    return parts[0], parts[1]


def _extract_instance_network(instance: compute_v1.Instance) -> tuple[str | None, str | None]:
    private_ip: str | None = None
    public_ip: str | None = None
    if instance.network_interfaces:
        nic = instance.network_interfaces[0]
        private_ip = nic.network_i_p
        if nic.access_configs:
            public_ip = nic.access_configs[0].nat_i_p
    return public_ip, private_ip


def list_instances() -> list[InstanceInfo]:
    settings = get_settings()
    instances_client = get_instances_client()
    request = compute_v1.AggregatedListInstancesRequest(
        project=settings.gcp_project_id,
        filter=f'labels.project = "{settings.project}"',
    )

    instances: list[InstanceInfo] = []
    for scope, scoped_list in instances_client.aggregated_list(request=request):
        if not scoped_list.instances:
            continue
        zone = scope.split("/")[-1]
        for inst in scoped_list.instances:
            labels = dict(inst.labels or {})
            if labels.get("project") != settings.project:
                continue
            public_ip, private_ip = _extract_instance_network(inst)
            launch_time = None
            if inst.creation_timestamp:
                launch_time = datetime.fromisoformat(
                    inst.creation_timestamp.replace("Z", "+00:00")
                )
            instances.append(
                InstanceInfo(
                    instance_id=f"{zone}:{inst.name}",
                    name=labels.get("name", inst.name),
                    instance_type=inst.machine_type.split("/")[-1],
                    state=inst.status.lower(),
                    public_ip=public_ip,
                    private_ip=private_ip,
                    launch_time=launch_time,
                    zone=zone,
                    tags=labels,
                )
            )

    return sorted(instances, key=lambda item: (item.zone or "", item.name))


def start_instance(instance_id: str) -> dict[str, Any]:
    settings = get_settings()
    zone, name = _parse_instance_ref(instance_id)
    operation = get_instances_client().start(
        project=settings.gcp_project_id,
        zone=zone,
        instance=name,
    )
    _wait_for_operation(operation)
    return {"zone": zone, "instance": name, "status": "starting"}


def stop_instance(instance_id: str) -> dict[str, Any]:
    settings = get_settings()
    zone, name = _parse_instance_ref(instance_id)
    operation = get_instances_client().stop(
        project=settings.gcp_project_id,
        zone=zone,
        instance=name,
    )
    _wait_for_operation(operation)
    return {"zone": zone, "instance": name, "status": "stopping"}


def get_cost_estimate() -> CostEstimate:
    settings = get_settings()
    if not settings.billing_export_table:
        return CostEstimate(total_monthly=0.0, breakdown={})

    query = f"""
    SELECT
      service.description AS service,
      SUM(cost + IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS total
    FROM `{settings.billing_export_table}`
    WHERE usage_start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    GROUP BY service
    ORDER BY total DESC
    """

    try:
        rows = list(get_bigquery_client().query(query).result())
    except Exception:
        return CostEstimate(total_monthly=0.0, breakdown={})

    breakdown = {row["service"]: float(row["total"]) for row in rows}
    total = float(sum(breakdown.values()))
    return CostEstimate(total_monthly=total, breakdown=breakdown)


def list_gcs_results(bucket_name: str) -> list[dict[str, Any]]:
    storage_client = get_storage_client()
    try:
        blobs = storage_client.list_blobs(bucket_name, prefix="results/")
        return [
            {
                "key": blob.name,
                "size": blob.size or 0,
                "last_modified": (
                    blob.updated.astimezone(UTC).isoformat() if blob.updated else None
                ),
            }
            for blob in blobs
        ]
    except Exception:
        return []


def get_gcs_object(bucket_name: str, key: str) -> bytes:
    bucket = get_storage_client().bucket(bucket_name)
    blob = bucket.blob(key)
    return blob.download_as_bytes()
