from __future__ import annotations

import random
from abc import ABC, abstractmethod

from core.types import Query


class BaseBenchmark(ABC):
    task_type: str = "mcq"   # "mcq" | "open"
    name: str = "base"

    def __init__(self, n_samples: int = 100, seed: int = 42) -> None:
        self.n_samples = n_samples
        self.seed = seed
        self._queries: list[Query] | None = None

    def load(self) -> list[Query]:
        """Load dataset and return n_samples queries (reproducible via seed)."""
        if self._queries is not None:
            return self._queries
        all_queries = self._load_all()
        rng = random.Random(self.seed)
        if len(all_queries) > self.n_samples:
            all_queries = rng.sample(all_queries, self.n_samples)
        self._queries = all_queries
        return self._queries

    @abstractmethod
    def _load_all(self) -> list[Query]:
        """Return ALL available queries before sampling."""

    def is_correct(self, response_text: str | None, query: Query) -> bool:
        """Default: case-insensitive prefix match against query.answer."""
        if response_text is None or query.answer is None:
            return False
        return response_text.strip().upper().startswith(query.answer.strip().upper())
