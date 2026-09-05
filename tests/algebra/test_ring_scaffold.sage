"""Z/4Z as a ring object: negation, subtraction, both units, the quotient Z/6Z -> Z/3Z, and a semiring that is not a ring."""

import pytest

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import Rings, Semirings
from sage_categories.cat.calculus import binary_product_data


def residue_operations(modulus):
    carrier = Sets(tuple(range(modulus)))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    return carrier, addition, zero, multiplication, one


def test_residue_ring_operations() -> None:
    rings = Rings(Sets())
    _, addition, zero, multiplication, one = residue_operations(4)
    ring = rings(addition, zero, multiplication, one)
    assert ring in rings
    assert ring in rings.Commutative()
    assert ring.zero().datum() == 0
    assert ring.one().datum() == 1
    minus_one = -ring.point(1)
    assert minus_one.parent() is ring
    assert minus_one.datum() == 3
    assert (minus_one * minus_one).datum() == 1
    assert (ring.point(2) * ring.point(2)).datum() == 0
    assert (ring.point(1) - ring.point(3)).datum() == 2
    assert ask(ring.point(2) + ring.point(2) == ring.zero()) is True
    # The two legs are retained and reach one additive monoid: the semiring's additive copy is the group's monoid, renamed.
    additive = rings.factor(0).to_additive().on_object(rings.to_semiring().on_object(ring))
    group = rings.to_additive_group().on_object(ring)
    assert ring.family_component(2) is additive
    assert rings.factor(1).ambient().to_named_monoids().on_object(group) is additive


def test_quotient_ring_homomorphism() -> None:
    rings = Rings(Sets())
    six, three = residue_operations(6), residue_operations(3)
    residue_six, residue_three = rings(*six[1:]), rings(*three[1:])
    reduction = Mor(Sets)(six[0], three[0])(lambda value: value % 3)
    quotient = rings.homomorphism(residue_six, residue_three, reduction)
    assert quotient in Mor(rings)(residue_six, residue_three)
    assert quotient(residue_six.point(4)).datum() == 1
    assert quotient(residue_six.point(5) * residue_six.point(5)).datum() == 1
    assert ask(quotient(-residue_six.point(2)) == -quotient(residue_six.point(2))) is True
    assert ask(quotient(residue_six.one()) == residue_three.one()) is True


def test_boolean_semiring_is_not_a_ring() -> None:
    carrier = Sets((0, 1))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    disjunction = Mor(Sets)(square, carrier)(lambda pair: max(pair))
    conjunction = Mor(Sets)(square, carrier)(lambda pair: min(pair))
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    assert Semirings(Sets())(disjunction, zero, conjunction, one) in Semirings(Sets())
    # 1 has no additive inverse under disjunction, so the additive monoid is not a group.
    with pytest.raises(AssertionError):
        Rings(Sets())(disjunction, zero, conjunction, one)


test_residue_ring_operations()
test_quotient_ring_homomorphism()
test_boolean_semiring_is_not_a_ring()
