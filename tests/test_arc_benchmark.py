from benchmarks.arc import _choice_index, _normalize_choice_label


def test_arc_normalizes_alpha_answer_key():
    assert _normalize_choice_label("E") == "E"


def test_arc_normalizes_numeric_answer_key():
    assert _normalize_choice_label("5") == "E"


def test_arc_maps_extended_choice_index():
    assert _choice_index("E") == 4
