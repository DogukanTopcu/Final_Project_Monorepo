from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["benchmarks"])

BENCHMARKS = [
    {
        "id": "mmlu",
        "name": "MMLU",
        "description": "Massive Multitask Language Understanding",
        "categories": [
            "stem",
            "humanities",
            "social_sciences",
            "other",
        ],
        "total_samples": 14042,
        "suggested_sizes": [50, 100, 200, 500, 1000],
    },
    {
        "id": "arc",
        "name": "ARC",
        "description": "AI2 Reasoning Challenge",
        "categories": ["easy", "challenge"],
        "total_samples": 7787,
        "suggested_sizes": [50, 100, 200, 500],
    },
    {
        "id": "eats",
        "name": "EATS",
        "description": "Efficiency-Accuracy Trade-off Score",
        "categories": ["composite"],
        "total_samples": 5000,
        "suggested_sizes": [50, 100, 200],
    },
]


@router.get("/benchmarks")
async def list_benchmarks():
    return BENCHMARKS


@router.get("/benchmarks/{benchmark_id}")
async def get_benchmark(benchmark_id: str):
    for b in BENCHMARKS:
        if b["id"] == benchmark_id:
            return b
    return {"error": "Benchmark not found"}
