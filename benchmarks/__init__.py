from benchmarks.base import BaseBenchmark
from benchmarks.mmlu import MMLUBenchmark
from benchmarks.arc import ARCBenchmark
from benchmarks.hellaswag import HellaSwagBenchmark
from benchmarks.gsm8k import GSM8KBenchmark
from benchmarks.truthfulqa import TruthfulQABenchmark
from benchmarks.custom_stratified import CustomStratifiedBenchmark


def get_benchmark(name: str, n_samples: int = 100, seed: int = 42) -> BaseBenchmark:
    bench_map = {
        "mmlu":       MMLUBenchmark,
        "arc":        ARCBenchmark,
        "hellaswag":  HellaSwagBenchmark,
        "gsm8k":      GSM8KBenchmark,
        "truthfulqa": TruthfulQABenchmark,
        "custom_stratified": CustomStratifiedBenchmark,
    }
    cls = bench_map.get(name)
    if cls is None:
        raise ValueError(f"Unknown benchmark: {name!r}. Choose from {list(bench_map)}")
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
