"""Magmas over the cartesian monoidal structure on sets: an asymmetric product and a homomorphism."""

from sage_categories.all import Cat, Fun, Mor, Sets, Cartesian, ask
from sage_categories.cat.structured_objects import Magmas
from sage_categories.cat.calculus import binary_product_data


def test_left_zero_magma_and_nonidentity_homomorphism() -> None:
    carrier = Sets((0, 1, 2))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), carrier, carrier).apex()

    left_zero = Mor(Sets)(square, carrier)(lambda pair: pair[0])
    right_zero = Mor(Sets)(square, carrier)(lambda pair: pair[1])
    assert ask(left_zero(square.point((1, 2))) == carrier.point(1)) is True
    assert ask(left_zero(square.point((1, 2))) == right_zero(square.point((1, 2)))) is False

    magma = Magmas(structure).algebra(carrier, left_zero)
    assert magma in Magmas(structure)
    assert magma.carrier() is carrier

    swap = Mor(Sets)(carrier, carrier)(lambda value: {0: 1, 1: 0, 2: 2}[value])
    homomorphism = Magmas(structure).homomorphism(magma, magma, swap)
    forgetful = Magmas(structure).forgetful()
    assert forgetful.on_object(magma) is carrier
    image = forgetful.on_morphism(homomorphism)(carrier.point(0))
    assert image.parent() is carrier
    assert image.datum() == 1
    assert forgetful.on_morphism(homomorphism)(carrier.point(2)).datum() == 2


test_left_zero_magma_and_nonidentity_homomorphism()
