"""Z/3Z as an additive monoid and as a multiplicative monoid on one carrier: renamed generators, points, and a homomorphism."""

from sage_categories.all import Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import (
    AdditiveMagmas,
    AdditiveMonoids,
    Magmas,
    Monoids,
    MultiplicativeMonoids,
    PointedMagmas,
)
from sage_categories.cat.calculus import binary_product_data


def test_additive_and_multiplicative_monoids_on_one_carrier() -> None:
    carrier = Sets((0, 1, 2))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    multiplication = Mor(Sets)(square, carrier)(lambda pair: (pair[0] * pair[1]) % 3)
    zero = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), carrier)(lambda _: 1)

    additive = AdditiveMonoids(structure).renamed(Monoids(structure)(addition, zero))
    multiplicative = MultiplicativeMonoids(structure).renamed(Monoids(structure)(multiplication, one))
    assert additive in AdditiveMonoids(structure)
    assert multiplicative in MultiplicativeMonoids(structure)
    assert additive.addition() is addition
    assert multiplicative.multiplication() is multiplication

    # The renaming projection is the retained first leg of the product ``Monoids(V) × 1_+``.
    renaming = AdditiveMonoids(structure).product_projection(0)
    assert renaming.on_object(additive) is additive.neutral()
    assert additive.neutral() in Monoids(structure)
    assert additive.neutral() is not multiplicative.neutral()

    # Points carry the carrier's data and combine through the renamed operation.
    assert additive.zero().parent() is additive
    assert additive.zero().datum() == 0
    assert (additive.point(1) + additive.point(2)).datum() == 0
    assert (additive.point(2) + additive.point(2)).datum() == 1
    assert ask(additive.point(1) + additive.zero() == additive.point(1)) is True
    assert multiplicative.one().datum() == 1
    assert (multiplicative.point(2) * multiplicative.point(2)).datum() == 1
    assert (multiplicative.point(2) * multiplicative.point(0)).datum() == 0

    # Doubling is an automorphism of the additive monoid; its renamed image acts on renamed points.
    doubling = Mor(Sets)(carrier, carrier)(lambda value: (2 * value) % 3)
    neutral_monoid = additive.neutral()
    magma = Monoids(structure).to_magmas().on_object(neutral_monoid)
    magma_map = Magmas(structure).homomorphism(magma, magma, doubling)
    monoid_map = PointedMagmas(structure.tensor(), structure.unit()).homomorphism(neutral_monoid, neutral_monoid, magma_map)
    renamed_map = AdditiveMonoids(structure).homomorphism(additive, additive, monoid_map)
    assert renamed_map in Mor(AdditiveMonoids(structure))(additive, additive)
    assert renamed_map(additive.point(1)).datum() == 2
    assert renamed_map(additive.point(1) + additive.point(1)).datum() == (renamed_map(additive.point(1)) + renamed_map(additive.point(1))).datum()


def test_additive_magma_without_a_unit() -> None:
    carrier = Sets((0, 1, 2))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    first_projection = Mor(Sets)(square, carrier)(lambda pair: pair[0])

    magma = AdditiveMagmas(structure).renamed(Magmas(structure).algebra(carrier, first_projection))
    assert magma in AdditiveMagmas(structure)
    assert magma.addition() is first_projection
    assert (magma.point(2) + magma.point(1)).datum() == 2
    assert (magma.point(1) + magma.point(2)).datum() == 1
    assert AdditiveMagmas(structure).to_carrier().on_object(magma) is carrier


test_additive_and_multiplicative_monoids_on_one_carrier()
test_additive_magma_without_a_unit()
