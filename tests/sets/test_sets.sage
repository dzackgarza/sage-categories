"""``Sets()``: rule-defined sets, finite enumerations, maps, isomorphisms, and cardinals.

Oracles: a cardinality is exact or ``Unknown`` (POL-ASSUME-004); a subcategory monomorphism maps
by identity (POL-FUN-027); monomorphisms of sets are the injective maps (Mathlib
``CategoryTheory.mono_iff_injective``); equality handlers decide on their declared
domains (POL-MATH-034, POL-MATH-042).
"""

import pytest

from sage_categories.all import *


def _integers():
    """The set of Python integers, defined by rule and never enumerated."""
    return Sets()(lambda datum: type(datum) is int)


def test_finite_sets_declare_one_subcategory_monomorphism_and_receive_the_set_surface() -> None:
    into_sets = Sets().Finite().structure_functors()[int(0)]
    triple = Sets().Finite()((int(4), int(5), int(6)))
    five = triple.point(int(5))
    successor = Mor(Sets().Finite())(triple, triple)(lambda datum: int(4) + (datum - int(3)) % int(3))

    assert into_sets in Fun(Sets().Finite(), Sets()).Monomorphisms().Isofibrations().Full()
    assert into_sets in Fun.Faithful()
    assert into_sets is Fun(Sets().Finite(), Sets()).Monomorphisms().Isofibrations().Full()()
    assert into_sets.on_object(triple) is triple
    assert into_sets.on_morphism(successor) is successor
    assert into_sets.on_element(five) is five

    assert triple in Sets().Finite()
    assert triple in Sets()
    assert five in triple
    assert ask(triple.cardinality() == int(3))
    points = list(triple)
    assert len(points) == int(3)
    assert all(any(ask(point == triple.point(datum)) for point in points) for datum in (int(4), int(5), int(6)))
    assert ask(successor(five) == triple.point(int(6)))
    assert successor in Mor(Sets())


def test_a_finite_enumeration_lists_distinct_members() -> None:
    assert ask(Sets().Finite()((int(1), int(2))).cardinality() == int(2))
    with pytest.raises(AssertionError):
        Sets().Finite()((int(1), int(1)))


def test_a_finite_set_enumerated_by_owned_points_decides_membership_and_image() -> None:
    """A datum may be an owned point, whose ``==`` is a proposition rather than a decision.

    Oracles: distinct points of ``[2]`` are distinct members, so ``#{p_0, p_1} = 2``;
    a constant map has a one-element image (``Set.image_const`` on a nonempty domain).
    """
    three = Sets().Simplex(int(2))
    first, second, third = three.point(int(0)), three.point(int(1)), three.point(int(2))
    pair = Sets().Finite()((first, second))

    assert pair in Sets().Finite()
    assert ask(pair.cardinality() == int(2))
    assert pair.point(first) in pair
    assert ask(pair.membership_proposition(pair.point(second)))
    with pytest.raises(AssertionError):
        pair.point(third)

    constant = Mor(Sets())(pair, pair)(lambda datum: first)
    image = constant.image()

    assert image in Sets().Finite()
    assert ask(image.cardinality() == int(1))
    assert ask(image.membership_proposition(image.point(first)))
    assert image.monomorphism() in Mor(Sets())(image, pair).Monomorphisms()


def test_a_rule_defined_set_needs_no_enumeration_and_equals_itself_only() -> None:
    integers, other_integers = _integers(), _integers()

    assert integers.point(int(7)) in integers
    assert integers.point(int(7)) in other_integers
    assert integers.cardinality() is Unknown
    assert ask(integers == integers)
    assert ask(integers == other_integers) is Unknown
    assert ask(integers.is_finite()) is Unknown


def test_equality_with_a_candidate_outside_the_category_is_undecided() -> None:
    """``ask`` is total over the equality candidate, which accepts every input (POL-TYPE-004).

    A set and a real number are not equal by any algorithm the repository owns, and no
    handler decides the pair, so the proposition is undecided rather than false or an
    error (POL-ASSUME-004, POL-MATH-042).
    """
    assert ask(Sets().Terminal() == 2.5) is Unknown
    assert ask(Sets().Terminal() == "1") is Unknown
    assert ask(Sets().Simplex(int(1)).point(int(0)) == 2.5) is Unknown
    assert ask(Sets().Terminal() == Sets().Terminal())


def test_finite_set_map_equality_is_pointwise() -> None:
    three, four = Sets().Simplex(int(2)), Sets().Simplex(int(3))
    successor = Mor(Sets())(three, four)(lambda datum: datum + int(1))
    successor_again = Mor(Sets())(three, four)(lambda datum: (datum + int(1)) % int(4))
    shifted = Mor(Sets())(three, four)(lambda datum: datum)

    assert ask(successor == successor_again)
    assert not ask(successor == shifted)

    increment = Mor(Sets())(ZZ, ZZ)(lambda datum: datum + int(1))
    increment_again = Mor(Sets())(ZZ, ZZ)(lambda datum: datum + int(1))
    assert ask(increment(ZZ(int(2))) == ZZ(int(3)))
    assert ask(increment_again(ZZ(int(2))) == ZZ(int(3)))
    assert ask(increment == increment_again) is Unknown
    assert ask(increment == increment)


def test_injectivity_is_placement_in_the_monomorphism_category() -> None:
    two, three = Sets().Simplex(int(1)), Sets().Simplex(int(2))
    injection = Mor(Sets())(two, three)(lambda datum: datum + int(1))
    collapse = Mor(Sets())(three, two)(lambda datum: min(datum, int(1)))
    integers = _integers()
    increment = Mor(Sets())(integers, integers)(lambda datum: datum + int(1))

    assert injection not in Mor(Sets()).Monomorphisms()
    assert ask(injection.is_monomorphism())
    assert injection in Mor(Sets()).Monomorphisms()
    assert injection in Mor(Sets())(two, three).Monomorphisms()
    assert not ask(injection.is_epimorphism())
    assert ask(collapse.is_epimorphism())
    assert not ask(collapse.is_monomorphism())
    assert ask(increment.is_monomorphism()) is Unknown


def test_a_set_isomorphism_supplies_its_inverse_from_the_isomorphism_category() -> None:
    two, pair = Sets().Simplex(int(1)), Sets().Finite()((int(10), int(20)))
    swap = Mor(Sets())(two, pair).Isomorphisms()(lambda datum: int(10) * (datum + int(1)), lambda datum: datum // int(10) - int(1))
    inverse = swap.inverse()

    assert swap in Mor(Sets()).Isomorphisms()
    assert swap in Mor(Sets()).Monomorphisms()
    assert inverse in Mor(Sets())(pair, two).Isomorphisms()
    assert ask(inverse * swap == two.identity())
    assert ask(swap * inverse == pair.identity())
    assert inverse.inverse() is swap

    bijection = Mor(Sets())(two, two)(lambda datum: int(1) - datum)
    assert ask(bijection.is_isomorphism())
    assert ask(bijection.inverse() * bijection == two.identity())
    assert two.identity() in Mor(Sets()).Automorphisms()


def test_an_asserted_isomorphism_without_a_rule_has_a_symbolic_inverse() -> None:
    integers = _integers()
    shift = Mor(Sets())(integers, integers).Isomorphisms()(lambda datum: datum + int(1))
    symbolic = shift.inverse()

    assert symbolic in Mor(Sets())(integers, integers).Isomorphisms()
    assert symbolic.inverse() is shift
    assert ask(shift(integers.point(int(2))) == integers.point(int(3)))
    with pytest.raises(AssertionError):
        symbolic(integers.point(int(3)))


def test_cardinality_is_exact_or_unknown_and_assumptions_refine() -> None:
    triple = Sets().Finite()((int(1), int(2), int(3)))
    assert ask(triple.cardinality() == int(3))
    assert not ask(triple.cardinality() == int(4))
    assert ask(triple.is_countable())

    integers = _integers()
    assert integers.cardinality() is Unknown
    assert integers not in Sets().Finite()
    assume(integers.is_finite())
    assert integers in Sets().Finite()
    assert integers.cardinality() is Unknown
    assert ask(integers.is_countable())

    reals = Sets()(lambda datum: type(datum) is float)
    assert ask(reals.is_uncountable()) is Unknown
    Sets().Uncountable()(reals)
    assert ask(reals.is_infinite())
    assert not ask(reals.is_countable())


def test_cardinal_arithmetic_and_order() -> None:
    assert ask(Cardinal()(int(3)) + int(4) == int(7))
    assert ask(aleph0 + int(5) == aleph0)
    assert ask(int(3) * aleph0 == aleph0)
    assert Cardinal()(int(2)) ** aleph0 is continuum
    assert ask(continuum ** int(2) == continuum)
    assert ask(aleph0 < continuum)
    assert ask(Cardinal().aleph(int(1)) <= continuum)
    assert Cardinal().aleph(int(1)) is continuum
    assert ask(continuum.is_uncountable())
    assert ask(aleph0.is_countable())
    assert ask(Cardinal()(int(3)) <= int(5))
    assert not ask(int(5) < Cardinal()(int(3)))
    assert Cardinal().aleph(int(0)) is aleph0
