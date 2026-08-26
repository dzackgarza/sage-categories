"""``Ordinals()``: exact ordinal expressions, their order, alephs with ordinal indices.

Oracles (Mathlib, inspected 2026-08-26): ``Ordinal.natCast_lt_omega0`` for
``2 < omega0``; ``Ordinal.omega_lt_omega`` for ``omega0 < omega(1)``;
``Ordinal.nadd_comm`` for the commutativity of the natural sum;
``Ordinal.one_add_omega0`` (``1 + omega0 = omega0``, so ordinary addition is not
commutative: ``omega0 + 1`` and ``1 + omega0`` are distinct expressions whose
equality no exact handler decides); ``Ordinal.opow_zero``, ``Ordinal.zero_opow``,
``Ordinal.one_opow``, and finite evaluation; ``Cardinal.aleph_lt_aleph`` with
``Ordinal.natCast_lt_omega0`` for ``aleph(1) < aleph(omega0)``; ``Cardinal.ord_aleph``
for the initial ordinal; ``Ordinal.card_omega0``, ``Ordinal.card_add``,
``Ordinal.card_mul``, and ``Ordinal.card_opow_eq_of_omega0_le_left`` /
``_right`` for cardinalities, with ``Cardinal.add_eq_max`` and ``Cardinal.mul_eq_max``
for the cardinal arithmetic.
"""

import pytest

from sage_categories.all import *
from sage_categories.ordinals import omega, ordinal


def test_ordinal_order_is_decided_by_exact_handlers() -> None:
    assert ask(ordinal(int(2)) < omega0) is True
    assert ask(ordinal(int(2)) <= ordinal(int(3))) is True
    assert ask(ordinal(int(3)) < ordinal(int(3))) is False
    assert ask(omega0 <= omega0) is True
    assert ask(omega0 < omega0) is False
    assert ask(omega0 < omega(int(1))) is True
    assert ask(omega(int(1)) <= omega0) is False
    assert ask(omega0 <= ordinal(int(5))) is False
    assert ask(omega0 <= omega0.ordinal_sum(int(1))) is Unknown
    with pytest.raises(TypeError):
        bool(omega0 < omega(int(1)))


def test_natural_sum_is_commutative_and_ordinary_sum_retains_its_order() -> None:
    assert ask(omega0 + int(1) == int(1) + omega0) is True
    assert hash(omega0 + int(1)) == hash(int(1) + omega0)
    assert ask(ordinal(int(2)) + int(3) == int(5)) is True
    assert ask(ordinal(int(2)) * int(3) == int(6)) is True

    left, right = omega0.ordinal_sum(int(1)), ordinal(int(1)).ordinal_sum(omega0)
    assert left is not right
    assert ask(left == right) is Unknown
    assert ask(left == omega0) is Unknown
    assert repr(left) == "(ω_0 +o 1)"
    assert repr(right) == "(1 +o ω_0)"


def test_ordinary_arithmetic_evaluates_finite_inputs_and_unit_laws() -> None:
    assert ask(ordinal(int(2)).ordinal_sum(int(3)) == int(5)) is True
    assert ask(ordinal(int(2)).ordinal_product(int(3)) == int(6)) is True
    assert ask(ordinal(int(2)).ordinal_power(int(3)) == int(8)) is True
    assert omega0.ordinal_sum(int(0)) is omega0
    assert ordinal(int(0)).ordinal_sum(omega0) is omega0
    assert omega0.ordinal_product(int(1)) is omega0
    assert omega0.ordinal_product(int(0)) is Ordinals().zero()
    assert omega0.ordinal_power(int(0)) is Ordinals().one()
    assert ordinal(int(0)).ordinal_power(omega0) is Ordinals().zero()
    assert ordinal(int(1)).ordinal_power(omega0) is Ordinals().one()


def test_initial_ordinals_and_ordinal_indexed_alephs() -> None:
    assert omega(int(0)) is omega0
    assert omega(omega0).initial_index() is omega0
    assert ask(omega0.is_initial()) is True
    assert ask(ordinal(int(3)).is_initial()) is False
    assert ask(ordinal(int(1)).ordinal_sum(omega0).is_initial()) is Unknown

    assert Cardinal().aleph(omega0).aleph_index() is omega0
    assert Cardinal().aleph(int(1)).aleph_index() is ordinal(int(1))
    assert Cardinal().aleph(int(0)) is aleph0
    assert Cardinal().aleph(omega0).initial_ordinal() is omega(omega0)
    assert ask(Cardinal().aleph(int(1)) < Cardinal().aleph(omega0)) is True
    assert ask(aleph0 < Cardinal().aleph(omega0)) is True
    assert ask(Cardinal().aleph(omega0) <= Cardinal().aleph(int(1))) is False
    assert ask(Cardinal().aleph(omega0).is_countable()) is False
    assert ask(Cardinal().aleph(omega0).is_uncountable()) is True


def test_ordinal_cardinalities() -> None:
    assert omega0.cardinality() is aleph0
    assert ordinal(int(5)).cardinality() is Cardinal()(int(5))
    assert (omega0 + int(1)).cardinality() is aleph0
    assert omega0.ordinal_sum(int(1)).cardinality() is aleph0
    assert (omega0 * omega0).cardinality() is aleph0
    assert omega(int(1)).ordinal_product(omega0).cardinality() is Cardinal().aleph(int(1))
    assert ordinal(int(2)).ordinal_power(omega0).cardinality() is aleph0
    assert omega0.ordinal_power(omega0).cardinality() is aleph0
    assert omega(int(1)).ordinal_power(int(2)).cardinality() is Cardinal().aleph(int(1))
    assert omega(omega0).cardinality() is Cardinal().aleph(omega0)
