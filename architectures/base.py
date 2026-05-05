from __future__ import annotations

import time
from abc import ABC, abstractmethod

from core.models import ModelProvider
from core.types import Query, Response


class BaseArchitecture(ABC):
    """
    All architectures expose a single run(query) → Response interface.
    The caller never needs to know which model(s) fired internally.
    """

    name: str = "base"

    def __init__(self, slm: ModelProvider, llm: ModelProvider) -> None:
        self.slm = slm
        self.llm = llm

    @abstractmethod
    def run(self, query: Query) -> Response:
        ...

    def _timed_generate(
        self, provider: ModelProvider, prompt: str, **kwargs
    ) -> tuple[str, float, int, int, float, float]:
        """Wraps generate() with wall-clock timing."""
        t0 = time.perf_counter()
        text, conf, in_tok, out_tok, cost = provider.generate(prompt, **kwargs)
        latency_ms = (time.perf_counter() - t0) * 1000
        return text, conf, in_tok, out_tok, cost, latency_ms
