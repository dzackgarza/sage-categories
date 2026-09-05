"""The additive monoid Z/3Z over sets, its doubling automorphism, and a unit counterexample."""

from sage_categories.all import Cat, Fun, Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import Monoids, Magmas
from sage_categories.cat.calculus import binary_product_data


def test_additive_monoid_and_doubling_automorphism() -> None:
    carrier = Sets((0, 1, 2))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    unit = Mor(Sets)(structure.unit(), carrier)(lambda _: 0)

    monoid = Monoids(structure)(addition, unit)
    assert monoid in Monoids(structure)
    assert monoid.carrier().carrier() is carrier
    assert ask(addition(square.point((2, 2))) == carrier.point(1)) is True

    magma = Monoids(structure).to_magmas().on_object(monoid)
    assert magma.carrier() is carrier
    doubling = Mor(Sets)(carrier, carrier)(lambda value: (2 * value) % 3)
    homomorphism = Magmas(structure).homomorphism(magma, magma, doubling)
    forgetful = Magmas(structure).forgetful()
    assert forgetful.on_morphism(homomorphism)(carrier.point(1)).datum() == 2
    assert ask(doubling(carrier.point(0)) == carrier.point(0)) is True


def test_incompatible_unit_fails_the_unit_equation() -> None:
    carrier = Sets((0, 1, 2))
    square = binary_product_data(Sets(), carrier, carrier).apex()
    addition = Mor(Sets)(square, carrier)(lambda pair: (pair[0] + pair[1]) % 3)
    # The left unit law for a candidate unit ``e`` states ``e + x == x`` for every ``x``.
    # The neutral element 0 satisfies it; the element 1 disproves it at ``x = 0``.
    assert ask(addition(square.point((0, 0))) == carrier.point(0)) is True
    assert ask(addition(square.point((1, 0))) == carrier.point(0)) is False
    assert ask(addition(square.point((1, 2))) == carrier.point(2)) is False


test_additive_monoid_and_doubling_automorphism()
test_incompatible_unit_fails_the_unit_equation()
