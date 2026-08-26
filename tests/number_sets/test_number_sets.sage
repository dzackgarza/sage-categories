"""The owned number sets ``NN``, ``ZZ``, ``QQ``, ``RR`` and maps between them.

Oracles: ``NN`` excludes zero by definition (POL-SET-032); the cardinalities are
Mathlib ``Cardinal.mk_pnat``, ``Cardinal.mk_int``, ``Cardinal.mkRat``, and
``Cardinal.mk_real`` with ``Cardinal.continuum = 2 ^ aleph0``; the floor of ``7/2``
is ``3`` by the definition of the floor (the greatest integer at most ``7/2``);
equality of rationals is equality of reduced fractions; D17 for map equality on a
rule-defined infinite domain.
"""

import pytest

from sage_categories.all import *


def test_the_positive_integers_exclude_zero() -> None:
    assert ZZ(1) in NN
    assert NN(1) in NN
    assert ZZ(0) not in NN
    assert ZZ(-1) not in NN
    with pytest.raises(AssertionError):
        NN(0)
    assert NN.cardinality() is aleph0


def test_the_number_sets_record_their_cardinalities_and_placements() -> None:
    assert ZZ.cardinality() is aleph0
    assert QQ.cardinality() is aleph0
    assert RR.cardinality() is continuum
    assert ZZ in Sets()
    assert ZZ in Sets().Countable()
    assert RR in Sets().Uncountable()
    assert ask(RR.is_uncountable()) is True
    assert ask(RR.is_countable()) is False
    assert ask(QQ.is_countable()) is True
    assert ask(ZZ.is_finite()) is False
    assert ask(ZZ.is_infinite()) is True


def test_membership_decides_exactly_for_supplied_data() -> None:
    assert ZZ(3) in ZZ
    assert ZZ(3) in QQ
    assert QQ(3) in ZZ
    assert QQ(1 / 2) in QQ
    assert QQ(1 / 2) not in ZZ
    assert ZZ(3) in RR
    assert QQ(1 / 2) in RR
    assert RR(3) in RR
    assert ZZ(3).parent() is ZZ
    assert QQ(3).parent() is QQ


def test_points_of_one_set_compare_by_their_exact_data() -> None:
    assert ask(QQ(1 / 2) == QQ(2 / 4)) is True
    assert hash(QQ(1 / 2)) == hash(QQ(2 / 4))
    assert ask(QQ(1 / 2) == QQ(1 / 3)) is False
    assert ask(ZZ(3) == ZZ(3)) is True
    assert ask(ZZ(3) == ZZ(4)) is False
    assert ask(RR(3) == RR(3)) is True
    assert ask(RR(3) == RR(1 / 2)) is False


def test_a_floor_map_from_the_rationals_needs_no_enumeration() -> None:
    floor = Mor(Sets())(QQ, ZZ)(lambda q: q.floor())
    floor_again = Mor(Sets())(QQ, ZZ)(lambda q: q.floor())

    assert floor.domain() is QQ
    assert floor.codomain() is ZZ
    assert floor in Mor(Sets())(QQ, ZZ)
    assert ask(floor(QQ(7 / 2)) == ZZ(3)) is True
    assert ask(floor(QQ(-7 / 2)) == ZZ(-4)) is True
    assert floor(QQ(7 / 2)).parent() is ZZ
    assert ask(floor == floor) is True
    assert ask(floor == floor_again) is Unknown


def test_maps_between_the_number_sets_are_ordinary_set_maps() -> None:
    square = Mor(Sets())(RR, RR)(lambda x: x * x)
    into_naturals = Mor(Sets())(QQ, NN)(lambda q: q.numerator().abs() + 1)
    include = Mor(Sets())(NN, ZZ)(lambda n: n)

    assert ask(square(RR(3)) == RR(9)) is True
    assert ask(into_naturals(QQ(-2 / 3)) == NN(3)) is True
    assert ask((include * into_naturals)(QQ(-2 / 3)) == ZZ(3)) is True
    assert (include * into_naturals).domain() is QQ
    assert (include * into_naturals).codomain() is ZZ
