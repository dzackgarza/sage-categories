"""Finite subsets, subsets of a fixed size, finitely supported functions, and their cardinalities.

Oracles: ``[4] = {0, 1, 2, 3, 4}`` has ``2 ** 5 = 32`` subsets (Mathlib ``Finset.card_powerset``)
and ``C(5, 2) = 10`` of size ``2`` (``Finset.card_powersetCard``); the finite subsets of an
infinite set have its cardinality (``Cardinal.mk_finset_of_infinite``), as do the subsets
of a fixed positive size (the embedding sandwich of ``sets/finite_subsets.py``); the
finite subsets of a countable set are countable (``Finset.countable``); a subset of ``X``
is a chosen subobject with its inclusion (POL-FUN-013); Sage's ``Subsets`` enumerates in
rank order with ``{}`` first and the whole set last; ``#(S →₀ X) = (#X) ** (#S)`` for
finite ``S`` (``Cardinal.mk_finsupp_lift_of_fintype``) and ``max(#S, #X)`` for infinite
``S`` and ``#X >= 2`` (``Cardinal.mk_finsupp_of_infinite``); a countable infinite set has
cardinality ``aleph0`` (``Cardinal.mk_eq_aleph0``).
"""

import pytest

from sage_categories.all import *


def _five():
    return Sets().Simplex(int(4))


def test_the_finite_subsets_of_an_enumerated_set_are_enumerated_and_select_subobjects() -> None:
    five = _five()
    subsets = Sets().FiniteSubsets()(five)

    assert subsets in Sets().FiniteSubsets()
    assert subsets in Sets().Finite()
    assert subsets.base_set() is five
    assert ask(subsets.cardinality() == int(32)) is True
    assert Sets().FiniteSubsets()(five) is subsets

    first, last = subsets[int(0)], subsets[int(31)]
    assert first in Sets().ChosenSubsets()
    assert first.underlying_set() is five
    assert ask(first.cardinality() == int(0)) is True
    assert ask(last.cardinality() == int(5)) is True
    assert last.monomorphism() in Mor(Sets())(last, five).Monomorphisms()
    assert ask(subsets.index(last) == int(31)) is True
    assert ask(subsets.index(first) == int(0)) is True

    odd = five.subset_from(lambda datum: datum % int(2) == int(1))
    point = subsets.point_of(odd)
    assert point in subsets
    assert point.parent() is subsets
    selected = subsets.subset_at(point)
    assert selected in Sets().Finite()
    assert ask(selected.cardinality() == int(2)) is True
    assert five.point(int(3)) in selected
    assert five.point(int(2)) not in selected
    assert ask(selected <= odd) is True and ask(odd <= selected) is True
    assert subsets[subsets.index(odd)] is selected
    assert ask(subsets.point_of(selected) == point) is True
    assert ask(subsets.point_of(odd) == subsets.point_of(five.subset_from(lambda datum: datum == int(0)))) is False
    with pytest.raises(AssertionError):
        subsets.point_of(ZZ.subset_from(lambda n: n > int(0)))


def test_subsets_of_a_fixed_size_have_the_binomial_count_and_inherit_the_finite_subset_surface() -> None:
    five = _five()
    pairs = Sets().SubsetsOfSize(int(2))(five)

    assert pairs in Sets().SubsetsOfSize(int(2))
    assert pairs in Sets().FiniteSubsets()
    assert pairs is not Sets().FiniteSubsets()(five)
    assert pairs.base_set() is five
    assert ask(pairs.subset_cardinality() == int(2)) is True
    assert ask(pairs.cardinality() == int(10)) is True
    assert ask(Sets().SubsetsOfSize(int(0))(five).cardinality() == int(1)) is True
    assert ask(Sets().SubsetsOfSize(int(5))(five).cardinality() == int(1)) is True
    assert ask(Sets().SubsetsOfSize(int(6))(five).cardinality() == int(0)) is True

    first = pairs[int(0)]
    assert ask(first.cardinality() == int(2)) is True
    assert five.point(int(0)) in first and five.point(int(1)) in first
    assert ask(pairs.index(first) == int(0)) is True
    top = five.subset_from(lambda datum: datum >= int(3))
    assert ask(pairs.index(top) == int(9)) is True
    assert pairs.subset_at(pairs.point_of(top)) is pairs[int(9)]
    assert Sets().SubsetsOfSize(int(2)) is Sets().SubsetsOfSize(int(2))
    assert Sets().SubsetsOfSize(int(2)) is not Sets().SubsetsOfSize(int(3))


def test_finite_subsets_of_an_infinite_set_have_its_cardinality_and_no_induced_enumeration() -> None:
    finite = Sets().FiniteSubsets()(ZZ)
    pairs = Sets().SubsetsOfSize(int(2))(ZZ)
    singletons = Sets().SubsetsOfSize(int(1))(RR)

    assert finite.cardinality() is aleph0
    assert finite in Sets().Countable()
    assert pairs.cardinality() is aleph0
    assert singletons.cardinality() is continuum
    assert Sets().SubsetsOfSize(int(0))(RR).cardinality() is Cardinal()(int(1))
    assert Sets().FiniteSubsets()(Sets()(lambda datum: type(datum) is int)).cardinality() is Unknown

    point = finite.point_of(Sets().ChosenSubsets().from_enumeration(ZZ, (int(3), int(-1))))
    subset = finite.subset_at(point)
    assert subset in Sets().Finite()
    assert subset.underlying_set() is ZZ
    assert ask(subset.cardinality() == int(2)) is True
    assert ZZ(int(3)) in subset
    assert ZZ(int(4)) not in subset
    assert ask(pairs.membership_proposition(point)) is True
    assert ask(pairs.membership_proposition(pairs.point_of(subset))) is True
    assert ask(pairs.membership_proposition(finite.point_of(Sets().ChosenSubsets().from_enumeration(ZZ, (int(1), int(2), int(3)))))) is False
    with pytest.raises(AssertionError):
        finite[int(0)]
    with pytest.raises(AssertionError):
        finite.point_of(ZZ.subset_from(lambda n: n > int(0)))


def test_finitely_supported_functions_retain_their_pointed_data_and_cardinalities() -> None:
    three, four = Sets().Simplex(int(2)), Sets().Simplex(int(3))
    functions = Sets().FinitelySupportedFunctions()(three, four.point(int(0)))

    assert functions in Sets().FinitelySupportedFunctions()
    assert functions in Sets().ChosenSubsets()
    assert functions.index_set() is three
    assert functions.value_set() is four
    assert functions.basepoint() is four.point(int(0))
    assert functions.underlying_set() is four ** three
    assert functions.monomorphism() in Mor(Sets())(functions, four ** three).Monomorphisms()
    assert ask(functions.cardinality() == int(64)) is True
    name = Sets().name_of(Mor(Sets())(three, four)(lambda datum: datum + int(1)))
    assert name in functions
    assert Sets().FinitelySupportedFunctions()(three, four.point(int(0))) is functions

    sequences = Sets().FinitelySupportedFunctions()(NN, ZZ(int(0)))
    assert sequences.index_set() is NN
    assert sequences.cardinality() is aleph0
    assert Sets().FinitelySupportedFunctions()(RR, ZZ(int(0))).cardinality() is continuum
    assert Sets().FinitelySupportedFunctions()(NN, Sets().Terminal().point(())).cardinality() is Cardinal()(int(1))
    assert ask(sequences.membership_proposition(Sets().name_of(Mor(Sets())(NN, ZZ)(lambda n: n)))) is Unknown
    assert Sets().name_of(Mor(Sets())(NN, ZZ)(lambda n: n)) in ZZ ** NN


def test_a_countable_infinite_set_has_cardinality_aleph_zero_by_placement() -> None:
    even = ZZ.subset_from(lambda n: n % 2 == 0)
    assert even.cardinality() is Unknown
    assert even in Sets().Countable()
    assume(even.is_infinite())
    assert even in Sets().Infinite()
    assert even.cardinality() is aleph0
    assert ask(even.is_countable()) is True
