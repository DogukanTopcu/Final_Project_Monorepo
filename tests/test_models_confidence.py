from __future__ import annotations

from core.models import OllamaModel


def test_ollama_confidence_heuristic_spreads_values():
    model = OllamaModel("gemma4:latest")

    slower = model._estimate_confidence(
        {
            "eval_count": 20,
            "prompt_eval_count": 120,
            "eval_duration": 2_500_000_000,
            "prompt_eval_duration": 1_600_000_000,
        }
    )
    faster = model._estimate_confidence(
        {
            "eval_count": 20,
            "prompt_eval_count": 120,
            "eval_duration": 600_000_000,
            "prompt_eval_duration": 450_000_000,
        }
    )

    assert 0.18 <= slower <= 0.92
    assert 0.18 <= faster <= 0.92
    assert faster > slower
