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
    ) -> tuple[str, float | None, int, int, float, float]:
        """Wraps generate() and prefers model-reported inference latency."""
        t0 = time.perf_counter()
        text, conf, in_tok, out_tok, cost = provider.generate(prompt, **kwargs)
        wall_latency_ms = (time.perf_counter() - t0) * 1000
        metadata = getattr(provider, "last_generation_metadata", {})
        if isinstance(metadata, dict):
            metadata["wall_latency_ms"] = wall_latency_ms
        server_latency_ms = (
            metadata.get("latency_ms_server")
            if isinstance(metadata, dict)
            else None
        )
        latency_ms = (
            float(server_latency_ms)
            if isinstance(server_latency_ms, (int, float)) and server_latency_ms > 0
            else wall_latency_ms
        )
        return text, conf, in_tok, out_tok, cost, latency_ms
