"""Z/6Z as a group object: the shear-map decision, inversion, subtraction, the quotient to Z/3Z, and two non-groups."""

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import AdditiveGroups, Groups, Magmas, Monoids, PointedMagmas
from sage_categories.cat.calculus import binary_product_data


def cyclic_monoid(modulus):
    carrier = Sets(tuple(range(modulus)))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % modulus)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    return carrier, Monoids(structure)(addition, zero)


def test_cyclic_group_inversion_and_subtraction() -> None:
    structure = Cartesian(Sets())
    carrier, monoid = cyclic_monoid(6)
    assert ask(monoid.is_group()) is True
    assert monoid in Groups(structure)
    inversion = monoid.inversion()
    assert inversion(carrier.point(2)).datum() == 4
    assert inversion(carrier.point(0)).datum() == 0
    assert ask(monoid.is_commutative()) is True
    assert monoid in Groups(structure).Commutative()

    group = AdditiveGroups(structure).renamed(monoid)
    assert group in AdditiveGroups(structure)
    assert group.negation() is inversion
    assert (-group.point(2)).datum() == 4
    assert (group.point(1) - group.point(3)).datum() == 4
    assert (group.point(4) + group.point(5)).datum() == 3
    assert group.zero().datum() == 0
    assert group in AdditiveGroups(structure).Commutative()


def test_quotient_homomorphism_preserves_negation() -> None:
    structure = Cartesian(Sets())
    six, monoid6 = cyclic_monoid(6)
    three, monoid3 = cyclic_monoid(3)
    assert ask(monoid3.is_group()) is True
    reduction = Mor(Sets)(six, three)(lambda value: value % 3)
    to_magmas = Monoids(structure).to_magmas()
    magma_map = Magmas(structure).homomorphism(to_magmas.on_object(monoid6), to_magmas.on_object(monoid3), reduction)
    monoid_map = PointedMagmas(structure.tensor(), structure.unit()).homomorphism(monoid6, monoid3, magma_map)
    assert monoid_map in Mor(Groups(structure))(monoid6, monoid3)
    group6, group3 = AdditiveGroups(structure).renamed(monoid6), AdditiveGroups(structure).renamed(monoid3)
    quotient = AdditiveGroups(structure).homomorphism(group6, group3, monoid_map)
    assert quotient(group6.point(4)).datum() == 1
    assert ask(quotient(-group6.point(2)) == -quotient(group6.point(2))) is True


def test_monoids_that_are_not_groups() -> None:
    structure = Cartesian(Sets())
    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % 3)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)
    multiplicative = Monoids(structure)(multiplication, one)
    # 0 has no multiplicative inverse, so the shear map (x, y) -> (x, xy) is not a bijection.
    assert ask(multiplicative.is_group()) is False
    assert ask(multiplicative.is_commutative()) is True
    left_zero = Magmas(structure).algebra(carrier, Mor(Sets)(square, carrier)(lambda pair: pair[0]))
    assert ask(left_zero.is_commutative()) is False


test_cyclic_group_inversion_and_subtraction()
test_quotient_homomorphism_preserves_negation()
test_monoids_that_are_not_groups()
