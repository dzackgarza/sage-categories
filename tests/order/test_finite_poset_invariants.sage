"""Complete finite-poset invariants reconstruct exact owned public results."""

import pytest
from sympy import false, true

from sage_categories.all import (
    Cardinal,
    FinitePosets,
    FiniteTotallyOrderedSets,
    Posets,
    Sets,
    ask,
)
from sage_categories.order.posets import BinaryRelations


def _poset(values, related):
    carrier = Sets(tuple(values))
    relation = BinaryRelations().from_predicate(
        carrier,
        lambda first, second: true if related(first.datum(), second.datum()) else false,
    )
    return FinitePosets()(relation.relation())


def _divisibility():
    return _poset((1, 2, 3, 6), lambda first, second: second % first == 0)


def _selected_data(ambient, subobject):
    family = Posets().Subobjects(ambient)
    inclusion = family.defining_arrow().on_object(subobject)
    return {inclusion(point).datum() for point in inclusion.domain()}


def test_covers_height_width_and_empty_values_are_owned() -> None:
    poset = _divisibility()
    one, two, six = (poset.point(value) for value in (1, 2, 6))

    assert ask(poset.covers(one, two)) is True
    assert ask(poset.covers(one, six)) is False
    assert ask(poset.covers(two, one)) is False
    assert poset.height() in Cardinal()
    assert poset.width() in Cardinal()
    assert ask(poset.height() == Cardinal()(3)) is True
    assert ask(poset.width() == Cardinal()(2)) is True

    empty = _poset((), lambda _first, _second: False)
    assert ask(empty.height() == Cardinal().zero()) is True
    assert ask(empty.width() == Cardinal().zero()) is True


def test_linear_extension_uses_the_exact_carrier_and_extends_the_order() -> None:
    poset = _divisibility()
    extension = poset.linear_extension()

    assert extension in FiniteTotallyOrderedSets()
    assert extension.carrier() is poset.carrier()
    for lower in poset:
        for upper in poset:
            if ask(lower <= upper) is True:
                assert ask(extension.point(lower.datum()) <= extension.point(upper.datum())) is True


def test_ranked_and_graded_properties_own_rank_and_level_sets() -> None:
    poset = _divisibility()
    one, two, three, six = (poset.point(value) for value in (1, 2, 3, 6))

    assert ask(poset.is_ranked()) is True
    assert poset in FinitePosets().Ranked()
    assert ask(poset.is_graded()) is True
    assert poset in FinitePosets().Graded()
    assert ask(poset.rank_of_element(one) == Cardinal()(0)) is True
    assert ask(poset.rank_of_element(two) == Cardinal()(1)) is True
    assert ask(poset.rank_of_element(three) == Cardinal()(1)) is True
    assert ask(poset.rank_of_element(six) == Cardinal()(2)) is True
    assert ask(poset.rank() == Cardinal()(2)) is True

    levels = poset.level_sets()
    shape = levels.domain()
    indices = shape.object_set()
    assert levels.codomain() is Posets().Subobjects(poset)
    assert tuple(point.datum() for point in indices) == (0, 1, 2)
    expected = ({1}, {2, 3}, {6})
    for index, data in enumerate(expected):
        level = levels.on_object(shape.object_at(indices.point(index)))
        assert level in Posets().Subobjects(poset)
        assert _selected_data(poset, level) == data

    graded = _divisibility()
    assert ask(graded.is_graded()) is True
    assert graded in FinitePosets().Graded()
    assert graded in FinitePosets().Ranked()
    assert ask(graded.rank() == Cardinal()(2)) is True


def test_bottom_and_top_exist_only_on_their_property_surfaces() -> None:
    poset = _divisibility()
    assert ask(poset.is_with_bottom()) is True
    assert ask(poset.is_with_top()) is True
    assert poset.bottom() is poset.point(1)
    assert poset.top() is poset.point(6)

    antichain = _poset((0, 1), lambda first, second: first == second)
    assert ask(antichain.is_with_bottom()) is False
    assert ask(antichain.is_with_top()) is False
    with pytest.raises(AttributeError):
        antichain.bottom
    with pytest.raises(AttributeError):
        antichain.top


test_covers_height_width_and_empty_values_are_owned()
test_linear_extension_uses_the_exact_carrier_and_extends_the_order()
test_ranked_and_graded_properties_own_rank_and_level_sets()
test_bottom_and_top_exist_only_on_their_property_surfaces()
