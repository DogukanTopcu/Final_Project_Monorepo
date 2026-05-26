from core.token_budget import compute_completion_budget


class _Provider:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id


def test_auto_budget_applies_slm_minimum_without_explicit_override():
    budget = compute_completion_budget(
        _Provider("qwen3.5-4b"),
        "Short MCQ prompt",
        task_type="mcq",
        role="slm_draft",
        requested_max_tokens=0,
    )
    assert budget == 128


def test_auto_budget_applies_llm_minimum_without_explicit_override():
    budget = compute_completion_budget(
        _Provider("llama3.3-70b"),
        "Short MCQ prompt",
        task_type="mcq",
        role="monolithic_llm",
        requested_max_tokens=0,
    )
    assert budget == 256


def test_explicit_max_tokens_still_wins_over_auto_minimum():
    budget = compute_completion_budget(
        _Provider("llama3.3-70b"),
        "Short prompt",
        task_type="open",
        role="monolithic_llm",
        requested_max_tokens=64,
    )
    assert budget == 64
