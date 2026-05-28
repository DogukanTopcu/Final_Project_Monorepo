from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["benchmarks"])

BENCHMARKS = [
    {
        "id": "mmlu",
        "name": "MMLU",
        "description": "Massive Multitask Language Understanding",
        "categories": ["stem", "humanities", "social_sciences", "other"],
        "total_samples": 14042,
        "suggested_sizes": [50, 100, 200, 500, 1000],
    },
    {
        "id": "arc",
        "name": "ARC",
        "description": "AI2 Reasoning Challenge",
        "categories": ["science", "mcq", "challenge"],
        "total_samples": 7787,
        "suggested_sizes": [50, 100, 200, 500],
    },
    {
        "id": "hellaswag",
        "name": "HellaSwag",
        "description": "Commonsense sentence completion benchmark",
        "categories": ["commonsense", "mcq"],
        "total_samples": 10042,
        "suggested_sizes": [50, 100, 200, 500],
    },
    {
        "id": "gsm8k",
        "name": "GSM8K",
        "description": "Grade school math reasoning benchmark",
        "categories": ["math", "open"],
        "total_samples": 1319,
        "suggested_sizes": [25, 50, 100, 200, 500],
    },
    {
        "id": "truthfulqa",
        "name": "TruthfulQA",
        "description": "Hallucination resistance multiple-choice benchmark",
        "categories": ["truthfulness", "mcq"],
        "total_samples": 817,
        "suggested_sizes": [25, 50, 100, 200],
    },
    {
        "id": "humaneval_plus",
        "name": "HumanEval+",
        "description": "164 function-completion problems with 80× augmented test cases (EvalPlus). Execution-based pass@1 scoring.",
        "categories": ["coding", "pass@1", "function-completion"],
        "total_samples": 164,
        "suggested_sizes": [20, 50, 100, 164],
    },
    {
        "id": "livecodebench",
        "name": "LiveCodeBench",
        "description": "Contamination-free competitive programming (LeetCode/AtCoder/Codeforces, post-training-cutoff). Execution-based pass@1 with easy/medium/hard split.",
        "categories": ["coding", "pass@1", "competitive", "easy", "medium", "hard"],
        "total_samples": 880,
        "suggested_sizes": [50, 100, 200, 500],
    },
    {
        "id": "custom_stratified",
        "name": "Custom Stratified (Deprecated)",
        "description": "Deprecated: MMLU+GSM8K difficulty mix, not a real coding benchmark. Use humaneval_plus or livecodebench instead.",
        "categories": ["deprecated"],
        "total_samples": 1000,
        "suggested_sizes": [30, 50, 100, 150, 300],
    },
]


@router.get("/benchmarks")
async def list_benchmarks():
    return BENCHMARKS


@router.get("/benchmarks/{benchmark_id}")
async def get_benchmark(benchmark_id: str):
    for benchmark in BENCHMARKS:
        if benchmark["id"] == benchmark_id:
            return benchmark
    return {"error": "Benchmark not found"}
