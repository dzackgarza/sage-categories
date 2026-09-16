"""Finite-poset ownership: inverse images, owned iteration, and monotone-map admission."""

import pytest
from sympy import false, true

from sage_categories.all import (
    FinitePosets,
    FiniteTotallyOrderedSets,
    Mor,
    Posets,
    Sets,
    TotallyOrderedSets,
    ask,
    order_preserving,
)
from sage_categories.order.posets import BinaryRelations


def _chain(size):
    carrier = Sets(tuple(range(size)))
    relation = BinaryRelations().from_predicate(
        carrier,
        lambda first, second: true if first.datum() <= second.datum() else false,
    )
    return Posets()(relation.relation())


def test_finite_posets_is_the_underlying_set_inverse_image() -> None:
    underlying = Posets().to_sets()
    finite = FinitePosets()
    assert finite is Posets().Finite()
    assert finite is underlying.inverse_image(Sets.Finite())
    assert finite.defining_functor() is underlying
    assert finite.target_subcategory() is Sets.Finite()


def test_finite_total_orders_are_the_finite_narrowing() -> None:
    finite_total = FiniteTotallyOrderedSets()
    assert finite_total is TotallyOrderedSets().Finite()
    assert finite_total is TotallyOrderedSets().property_subcategory(FinitePosets())
    assert finite_total is FinitePosets().property_subcategory(TotallyOrderedSets())
    targets = tuple(functor.codomain() for functor in finite_total.selected_functors())
    assert FinitePosets() in targets
    assert TotallyOrderedSets() in targets


def test_finite_iteration_returns_elements_of_the_original_poset() -> None:
    chain = _chain(4)
    finite = FinitePosets()
    assert chain in finite
    projection = finite.target_projection()
    assert projection.codomain() is Sets.Finite()
    assert projection.on_object(chain) is chain.carrier()
    points = tuple(chain)
    assert tuple(point.datum() for point in points) == (0, 1, 2, 3)
    assert all(point.parent() is chain for point in points)


def test_monotonicity_is_a_proposition_on_an_owned_set_morphism() -> None:
    source, target = _chain(3), _chain(2)
    underlying = Mor(Sets)(source.carrier(), target.carrier())(lambda value: min(value, 1))
    assert ask(order_preserving(source, target, underlying)) is True
    monotone = Mor(Posets())(source, target)(underlying)
    assert monotone.underlying_map() is underlying

    reversing = Mor(Sets)(target.carrier(), target.carrier())(lambda value: 1 - value)
    assert ask(order_preserving(target, target, reversing)) is False
    assert reversing in Mor(Sets)(target.carrier(), target.carrier())
    with pytest.raises(AssertionError):
        Mor(Posets())(target, target)(reversing)


def test_infinite_unestablished_map_does_not_gain_monotone_placement() -> None:
    integers = Sets.from_membership(lambda datum: true)
    relation = BinaryRelations().from_predicate(integers, lambda first, second: first == second)
    source = Posets()(relation.relation())
    underlying = Mor(Sets)(integers, integers)(lambda value: value)
    assert ask(order_preserving(source, source, underlying)) is not True
    with pytest.raises(AssertionError):
        Mor(Posets())(source, source)(underlying)


test_finite_posets_is_the_underlying_set_inverse_image()
test_finite_total_orders_are_the_finite_narrowing()
test_finite_iteration_returns_elements_of_the_original_poset()
test_monotonicity_is_a_proposition_on_an_owned_set_morphism()
test_infinite_unestablished_map_does_not_gain_monotone_placement()
