from core.prompt import mcq_prompt, parse_mcq_answer, parse_open_answer
from core.types import Query


def test_mcq_prompt_requests_final_answer_line_without_banning_explanations():
    query = Query(
        id="mmlu_1",
        text="What is 2 + 2?",
        choices=["1", "2", "3", "4"],
        answer="D",
    )

    prompt = mcq_prompt(query)

    assert "Do not include any explanation." not in prompt
    assert "Answer: <LETTER>" in prompt


def test_mcq_prompt_lists_dynamic_choice_range():
    query = Query(
        id="arc_1",
        text="Pick the best option.",
        choices=["A1", "B1", "C1", "D1", "E1"],
        answer="E",
    )

    prompt = mcq_prompt(query)

    assert "Choose the single best answer: A, B, C, D, E." in prompt


def test_parse_mcq_answer_accepts_answer_line_after_reasoning():
    text = "I checked the options carefully.\nAnswer: C"
    assert parse_mcq_answer(text) == "C"


def test_parse_mcq_answer_accepts_inline_explanatory_phrasing():
    text = "The answer is b because it matches the definition."
    assert parse_mcq_answer(text) == "B"


def test_parse_mcq_answer_accepts_markdown_bold_correct_answer():
    text = "The correct answer is **C**.\nHere is a breakdown of the reasoning."
    assert parse_mcq_answer(text) == "C"


def test_parse_mcq_answer_accepts_extended_choice_letters():
    text = "After checking all five choices, Answer: E"
    assert parse_mcq_answer(text) == "E"


def test_parse_mcq_answer_does_not_misread_options_heading():
    text = (
        "Here is a breakdown of the legal analysis:\n\n"
        "Analyzing the Options:\n"
        "A. First option\n"
        "B. Second option"
    )
    assert parse_mcq_answer(text) is None


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
