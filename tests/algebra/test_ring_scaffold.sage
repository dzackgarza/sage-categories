"""Z/4Z as a ring object: negation, subtraction, both units, the quotient Z/6Z -> Z/3Z, and a semiring that is not a ring."""

import pytest

from sage_categories.all import Cartesian, Mor, Sets, ask, parallel_pair
from sage_categories.cat.calculus import binary_product_data
from sage_categories.cat.cones import cone, cones
from sage_categories.cat.structured_objects import Rings, Semirings


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
    assert rings.structure_functors() == (rings.to_semiring(), rings.to_additive_group())
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
    forgetful = rings.forgetful()
    carrier_map = forgetful.on_morphism(quotient)
    assert carrier_map.domain() is forgetful.on_object(residue_six)
    assert carrier_map.codomain() is forgetful.on_object(residue_three)
    assert carrier_map(carrier_map.domain().point(5)).datum() == 2


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


def test_additive_nonunital_map_is_not_a_ring_map() -> None:
    rings = Rings(Sets())
    six = residue_operations(6)
    residue_six = rings(*six[1:])
    doubling = Mor(Sets)(six[0], six[0])(lambda value: (2 * value) % 6)
    additive_group = rings.to_additive_group().on_object(residue_six)
    additive = rings.factor(1).ambient()
    additive_map = additive.homomorphism(additive_group, additive_group, doubling)
    assert additive_map(additive_group.point(2)).datum() == 4
    with pytest.raises(AssertionError):
        rings.homomorphism(residue_six, residue_six, doubling)


def test_matrix_ring_opposite_reverses_multiplication_and_maps() -> None:
    rings = Rings(Sets())
    carrier = Sets(tuple((a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()

    def add(pair):
        return tuple((left + right) % 2 for left, right in zip(pair[0], pair[1], strict=True))

    def multiply(pair):
        a, b, c, d = pair[0]
        e, f, g, h = pair[1]
        return ((a * e + b * g) % 2, (a * f + b * h) % 2, (c * e + d * g) % 2, (c * f + d * h) % 2)

    addition = Mor(Sets)(square, carrier)(add)
    multiplication = Mor(Sets)(square, carrier)(multiply)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: (0, 0, 0, 0))
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: (1, 0, 0, 1))
    matrix_ring = rings(addition, zero, multiplication, one)
    opposite = rings.opposite_ring(matrix_ring)
    e12, e21 = matrix_ring.point((0, 1, 0, 0)), matrix_ring.point((0, 0, 1, 0))
    assert (e12 * e21).datum() == (1, 0, 0, 0)
    assert (e21 * e12).datum() == (0, 0, 0, 1)
    opposite_e12, opposite_e21 = opposite.point(e12.datum()), opposite.point(e21.datum())
    assert (opposite_e12 * opposite_e21).datum() == (e21 * e12).datum()

    identity_map = rings.homomorphism(matrix_ring, matrix_ring, Mor(Sets)(carrier, carrier).one())
    opposite_map = rings.opposite_functor().on_morphism(identity_map)
    assert opposite_map.domain() is opposite and opposite_map.codomain() is opposite
    assert opposite_map(opposite_e12).datum() == opposite_e12.datum()


def test_ring_products_and_equalizers_are_created_on_carriers() -> None:
    rings = Rings(Sets())
    two_data = residue_operations(2)
    two = rings(*two_data[1:])
    product = rings.Products()((two, two))
    first, second = product.product_projection(0), product.product_projection(1)
    assert first in Mor(rings)(product, two)
    assert second in Mor(rings)(product, two)
    off_diagonal = product.point((0, 1))
    assert first(off_diagonal).datum() == 0
    assert second(off_diagonal).datum() == 1
    assert (product.point((1, 1)) + product.point((1, 1))).datum() == (0, 0)

    diagram = parallel_pair(first, second)
    equalizer = rings.Limits(diagram.domain())(diagram)
    presentation = rings.Limits(diagram.domain()).universal_data(diagram)
    source = diagram.domain().generating_morphisms()[0].domain()
    projection = presentation.leg(source)
    diagonal_point = equalizer.point((1, 1))
    assert projection(diagonal_point).datum() == (1, 1)
    with pytest.raises(AssertionError):
        equalizer.point((0, 1))

    forgetful = rings.forgetful()
    diagonal_carrier = Mor(Sets)(forgetful.on_object(two), forgetful.on_object(product))(
        lambda value: (value, value)
    )
    diagonal = rings.homomorphism(two, product, diagonal_carrier)
    target_leg = first * diagonal
    candidate = cone(
        diagram,
        two,
        lambda vertex: diagonal if vertex is source else target_leg,
    )
    mediator = presentation.lift(cones(diagram)(candidate))
    assert ask(projection * mediator == diagonal) is True


test_residue_ring_operations()
test_quotient_ring_homomorphism()
test_boolean_semiring_is_not_a_ring()
test_additive_nonunital_map_is_not_a_ring_map()
test_matrix_ring_opposite_reverses_multiplication_and_maps()
test_ring_products_and_equalizers_are_created_on_carriers()
