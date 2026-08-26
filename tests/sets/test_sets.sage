"""``Sets()``: rule-defined sets, finite enumerations, maps, isomorphisms, and cardinals.

Oracles: the definitions of D01 (exact cardinal or ``Unknown``), D08 (inclusions map
by identity), D09 (monomorphisms of sets are the injective maps: Mathlib
``CategoryTheory.mono_iff_injective``), and D17 (equality handlers on their declared
domains).
"""

import pytest

from sage_categories.all import *


def _integers():
    """The set of Python integers, defined by rule and never enumerated."""
    return Sets()(lambda datum: type(datum) is int)


def test_finite_sets_declare_one_inclusion_and_receive_the_set_surface() -> None:
    inclusion = Sets().Finite().structure_functors()[int(0)]
    triple = Sets().Finite()((int(4), int(5), int(6)))
    five = triple.point(int(5))
    successor = Mor(Sets().Finite())(triple, triple)(lambda datum: int(4) + (datum - int(3)) % int(3))

    assert inclusion in Fun(Sets().Finite(), Sets()).FullyFaithful()
    assert inclusion.on_object(triple) is triple
    assert inclusion.on_morphism(successor) is successor
    assert inclusion.on_element(five) is five

    assert triple in Sets().Finite()
    assert triple in Sets()
    assert five in triple
    assert ask(triple.cardinality() == int(3)) is True
    points = list(triple)
    assert len(points) == int(3)
    assert all(any(ask(point == triple.point(datum)) is True for point in points) for datum in (int(4), int(5), int(6)))
    assert ask(successor(five) == triple.point(int(6))) is True
    assert successor in Mor(Sets())


def test_a_rule_defined_set_needs_no_enumeration_and_equals_itself_only() -> None:
    integers, other_integers = _integers(), _integers()

    assert integers.point(int(7)) in integers
    assert integers.point(int(7)) in other_integers
    assert integers.cardinality() is Unknown
    assert ask(integers == integers) is True
    assert ask(integers == other_integers) is Unknown
    assert ask(integers.is_finite()) is Unknown


def test_finite_set_map_equality_is_pointwise() -> None:
    three, four = Sets().Simplex(int(2)), Sets().Simplex(int(3))
    successor = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    successor_again = Mor(Sets())(three, four)(lambda datum: (datum + int(1)) % int(4))
    shifted = Mor(Sets())(three, four)(lambda datum: datum)

    assert ask(successor == successor_again) is True
    assert ask(successor == shifted) is False

    integers = _integers()
    increment = Mor(Sets())(integers, integers)(lambda datum: datum + int(1))
    increment_again = Mor(Sets())(integers, integers)(lambda datum: datum + int(1))
    assert ask(increment == increment_again) is Unknown
    assert ask(increment == increment) is True


def test_injectivity_is_placement_in_the_monomorphism_category() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    injection = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    collapse = Mor(Sets())(three, two)(lambda datum: min(datum, int(1)))
    integers = _integers()
    increment = Mor(Sets())(integers, integers)(lambda datum: datum + int(1))

    assert injection not in Mor(Sets()).Monomorphisms()
    assert ask(injection.is_monomorphism()) is True
    assert injection in Mor(Sets()).Monomorphisms()
    assert injection in Mor(Sets())(two, three).Monomorphisms()
    assert ask(injection.is_epimorphism()) is False
    assert ask(collapse.is_epimorphism()) is True
    assert ask(collapse.is_monomorphism()) is False
    assert ask(increment.is_monomorphism()) is Unknown


def test_a_set_isomorphism_supplies_its_inverse_from_the_isomorphism_category() -> None:
    two, pair = Sets().Simplex(int(1)), Sets().Finite()((int(10), int(20)))
    swap = Mor(Sets())(two, pair).Isomorphisms()(lambda datum: int(10) * (datum + int(1)), lambda datum: datum // int(10) - int(1))
    inverse = swap.inverse()

    assert swap in Mor(Sets()).Isomorphisms()
    assert swap in Mor(Sets()).Monomorphisms()
    assert inverse in Mor(Sets())(pair, two).Isomorphisms()
    assert ask(inverse * swap == two.identity()) is True
    assert ask(swap * inverse == pair.identity()) is True
    assert inverse.inverse() is swap

    bijection = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    assert ask(bijection.is_isomorphism()) is True
    assert ask(bijection.inverse() * bijection == two.identity()) is True
    assert two.identity() in Mor(Sets()).Automorphisms()


def test_cardinality_is_exact_or_unknown_and_assumptions_refine() -> None:
    triple = Sets().Finite()((int(1), int(2), int(3)))
    assert ask(triple.cardinality() == int(3)) is True
    assert ask(triple.cardinality() == int(4)) is False
    assert ask(triple.is_countable()) is True

    integers = _integers()
    assert integers.cardinality() is Unknown
    assert integers not in Sets().Finite()
    assume(integers.is_finite())
    assert integers in Sets().Finite()
    assert integers.cardinality() is Unknown
    assert ask(integers.is_countable()) is True

    reals = Sets()(lambda datum: type(datum) is float)
    assert ask(reals.is_uncountable()) is Unknown
    Sets().Uncountable()(reals)
    assert ask(reals.is_infinite()) is True
    assert ask(reals.is_countable()) is False


def test_cardinal_arithmetic_and_order() -> None:
    assert ask(Cardinal()(int(3)) + int(4) == int(7)) is True
    assert ask(aleph0 + int(5) == aleph0) is True
    assert ask(int(3) * aleph0 == aleph0) is True
    assert Cardinal()(int(2)) ** aleph0 is continuum
    assert ask(continuum ** int(2) == continuum) is True
    assert ask(aleph0 < continuum) is True
    assert ask(Cardinal().aleph(int(1)) <= continuum) is True
    assert ask(Cardinal().aleph(int(1)) == continuum) is Unknown
    assert ask(continuum.is_uncountable()) is True
    assert ask(aleph0.is_countable()) is True
    assert ask(Cardinal()(int(3)) <= int(5)) is True
    assert ask(int(5) < Cardinal()(int(3))) is False
    assert Cardinal().aleph(int(0)) is aleph0
