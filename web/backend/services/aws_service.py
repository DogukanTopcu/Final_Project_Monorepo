from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from web.backend.dependencies import get_ce_client, get_ec2_client, get_s3_client
from web.backend.schemas import CostEstimate, InstanceInfo


def list_instances() -> list[InstanceInfo]:
    ec2 = get_ec2_client()
    response = ec2.describe_instances(
        Filters=[{"Name": "tag:Project", "Values": ["thesis"]}]
    )
    instances: list[InstanceInfo] = []
    for reservation in response.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
            instances.append(
                InstanceInfo(
                    instance_id=inst["InstanceId"],
                    name=tags.get("Name", ""),
                    instance_type=inst["InstanceType"],
                    state=inst["State"]["Name"],
                    public_ip=inst.get("PublicIpAddress"),
                    private_ip=inst.get("PrivateIpAddress"),
                    launch_time=inst.get("LaunchTime"),
                    tags=tags,
                )
            )
    return instances


def start_instance(instance_id: str) -> dict[str, Any]:
    ec2 = get_ec2_client()
    response = ec2.start_instances(InstanceIds=[instance_id])
    return response["StartingInstances"][0]


def stop_instance(instance_id: str) -> dict[str, Any]:
    ec2 = get_ec2_client()
    response = ec2.stop_instances(InstanceIds=[instance_id])
    return response["StoppingInstances"][0]


def get_cost_estimate() -> CostEstimate:
    ce = get_ce_client()
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=30)

    try:
        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start.isoformat(),
                "End": end.isoformat(),
            },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        breakdown: dict[str, float] = {}
        total = 0.0
        for group in response.get("ResultsByTime", [{}])[0].get("Groups", []):
            service = group["Keys"][0]
            amount = float(group["Metrics"]["BlendedCost"]["Amount"])
            breakdown[service] = amount
            total += amount

        return CostEstimate(total_monthly=total, breakdown=breakdown)
    except Exception:
        return CostEstimate(total_monthly=0.0, breakdown={})


def list_s3_results(bucket: str) -> list[dict[str, Any]]:
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix="results/")
        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in response.get("Contents", [])
        ]
    except Exception:
        return []


def get_s3_object(bucket: str, key: str) -> bytes:
    s3 = get_s3_client()
    response = s3.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()
