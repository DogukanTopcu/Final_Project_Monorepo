from core.prompt import parse_open_answer


def test_parse_open_answer_accepts_explicit_answer_line():
    text = "Let's solve it.\nAnswer: 840"
    assert parse_open_answer(text) == "840"


def test_parse_open_answer_accepts_bare_numeric_last_line():
    text = "Work shown above.\n840"
    assert parse_open_answer(text) == "840"


def test_parse_open_answer_returns_none_for_truncated_reasoning():
    text = (
        "To solve this problem, let's break it down step by step.\n"
        "Cost of one dozen cups = $840\n"
        "Cost of one cup ="
    )
    assert parse_open_answer(text) is None


def test_parse_open_answer_does_not_fallback_to_last_intermediate_number():
    text = (
        "4. Since we want to find the cost of one cup, we need to divide the cost "
        "of one dozen cups by 12:\n"
        "Cost of one cup ="
    )
    assert parse_open_answer(text) is None
