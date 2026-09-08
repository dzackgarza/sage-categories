"""Presented terminal selection permits several terminal objects."""

from sage_categories.cat.canonical import FinitePresentedCategory


def test_two_isomorphic_vertices_are_both_terminal_but_one_is_selected() -> None:
    category = FinitePresentedCategory(
        "chaotic-two",
        ("left", "right"),
        (("forward", "left", "right"), ("backward", "right", "left")),
        ((("forward", "backward"), ()), (("backward", "forward"), ())),
    )
    selected = category.Terminal()
    assert selected is category("left")
    assert category.Terminal() is selected


test_two_isomorphic_vertices_are_both_terminal_but_one_is_selected()
