import warnings

from benchmarks.arc import ARCBenchmark
from benchmarks.base import BaseBenchmark
from benchmarks.custom_stratified import CustomStratifiedBenchmark
from benchmarks.gsm8k import GSM8KBenchmark
from benchmarks.hellaswag import HellaSwagBenchmark
from benchmarks.mmlu import MMLUBenchmark
from benchmarks.truthfulqa import TruthfulQABenchmark


def get_benchmark(name: str, n_samples: int = 100, seed: int = 42) -> BaseBenchmark:
    # Reasoning benchmarks
    _REASONING = {
        "mmlu":       MMLUBenchmark,
        "arc":        ARCBenchmark,
        "hellaswag":  HellaSwagBenchmark,
        "gsm8k":      GSM8KBenchmark,
        "truthfulqa": TruthfulQABenchmark,
    }
    # Deprecated
    _DEPRECATED = {
        "custom_stratified": CustomStratifiedBenchmark,
    }

    bench_map = {**_REASONING, **_DEPRECATED}

    if name in _DEPRECATED:
        warnings.warn(
            f"Benchmark {name!r} is deprecated: it is an MMLU+GSM8K difficulty mix.",
            DeprecationWarning,
            stacklevel=2,
        )

    cls = bench_map.get(name)
    if cls is None:
        raise ValueError(
            f"Unknown benchmark: {name!r}. "
            f"Available: {list(_REASONING)}."
        )
    return cls(n_samples=n_samples, seed=seed)


__all__ = [
    "BaseBenchmark",
    "MMLUBenchmark",
    "ARCBenchmark",
    "HellaSwagBenchmark",
    "GSM8KBenchmark",
    "TruthfulQABenchmark",
    "CustomStratifiedBenchmark",
    "get_benchmark",
]
