import warnings

from benchmarks.base import BaseBenchmark
from benchmarks.mmlu import MMLUBenchmark
from benchmarks.arc import ARCBenchmark
from benchmarks.hellaswag import HellaSwagBenchmark
from benchmarks.gsm8k import GSM8KBenchmark
from benchmarks.truthfulqa import TruthfulQABenchmark
from benchmarks.humaneval_plus import HumanEvalPlusBenchmark
from benchmarks.livecodebench import LiveCodeBenchBenchmark
from benchmarks.custom_stratified import CustomStratifiedBenchmark


def get_benchmark(name: str, n_samples: int = 100, seed: int = 42) -> BaseBenchmark:
    # Reasoning benchmarks
    _REASONING = {
        "mmlu":       MMLUBenchmark,
        "arc":        ARCBenchmark,
        "hellaswag":  HellaSwagBenchmark,
        "gsm8k":      GSM8KBenchmark,
        "truthfulqa": TruthfulQABenchmark,
    }
    # Coding benchmarks (literature-standard, execution-based)
    _CODING = {
        "humaneval_plus":  HumanEvalPlusBenchmark,
        "livecodebench":   LiveCodeBenchBenchmark,
    }
    # Deprecated
    _DEPRECATED = {
        "custom_stratified": CustomStratifiedBenchmark,
    }

    bench_map = {**_REASONING, **_CODING, **_DEPRECATED}

    if name in _DEPRECATED:
        warnings.warn(
            f"Benchmark {name!r} is deprecated: it is an MMLU+GSM8K difficulty mix, "
            "not a coding benchmark. Use 'humaneval_plus' or 'livecodebench' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    cls = bench_map.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown benchmark: {name!r}. "
            f"Reasoning: {list(_REASONING)}. "
            f"Coding: {list(_CODING)}."
        )
    return cls(n_samples=n_samples, seed=seed)


__all__ = [
    "BaseBenchmark",
    "MMLUBenchmark",
    "ARCBenchmark",
    "HellaSwagBenchmark",
    "GSM8KBenchmark",
    "TruthfulQABenchmark",
    "HumanEvalPlusBenchmark",
    "LiveCodeBenchBenchmark",
    "CustomStratifiedBenchmark",
    "get_benchmark",
]
