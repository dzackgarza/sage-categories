"""Coequalizers in Ab: the quotient of Z/4 by the image of the doubling map out of Z/2, and its mediator."""

from sage_categories.all import ask
from sage_categories.algebra import (
    AbelianGroups,
    abelian_homomorphism,
    coequalizer_mediator,
    coequalizer_projection,
    presented_abelian_group,
)


def test_coequalizer_of_zero_and_doubling_is_the_quotient_by_the_even_classes() -> None:
    two, four = AdditiveAbelianGroup([2]), AdditiveAbelianGroup([4])
    source, target = presented_abelian_group(two), presented_abelian_group(four)
    generator = four.gen(0)
    zero = abelian_homomorphism(source, target, lambda a: four.zero())
    double = abelian_homomorphism(source, target, lambda a: int(a.vector()[0]) * 2 * generator)

    quotient = coequalizer_projection(zero, double)
    apex = quotient.codomain()
    assert apex in AbelianGroups()
    assert quotient.domain() is target
    assert ask(quotient * zero == quotient * double) is True

    # The quotient identifies 2g with 0 and keeps g away from it, so the apex is Z/2.
    assert ask(quotient(target.point(2 * generator)) == apex.zero()) is True
    assert ask(quotient(target.point(generator)) == apex.zero()) is False
    assert ask(quotient(target.point(generator)) + quotient(target.point(generator)) == apex.zero()) is True

    # A map into (Z/2)^2 that kills 2g factors through the quotient by one homomorphism,
    # and that homomorphism is not the projection: it lands in a group of larger rank.
    pairs = AdditiveAbelianGroup([2, 2])
    plane = presented_abelian_group(pairs)
    corner = pairs.linear_combination_of_smith_form_gens(vector(ZZ, [1, 0]))
    coequalizing = abelian_homomorphism(target, plane, lambda x: int(x.vector()[0]) * corner)
    mediator = coequalizer_mediator(quotient, coequalizing)
    assert mediator.domain() is apex and mediator.codomain() is plane
    assert ask(mediator * quotient == coequalizing) is True
    assert ask(mediator(quotient(target.point(generator))) == plane.point(corner)) is True
    assert ask(mediator(apex.zero()) == plane.zero()) is True


def test_the_coequalizer_of_a_pair_that_is_already_equal_is_the_identity_on_the_target() -> None:
    six = AdditiveAbelianGroup([6])
    source, target = presented_abelian_group(six), presented_abelian_group(six)
    triple = abelian_homomorphism(source, target, lambda a: int(a.vector()[0]) * 3 * six.gen(0))
    quotient = coequalizer_projection(triple, triple)
    # Coequalizing f with itself imposes no relation, so the projection is an isomorphism
    # onto a group with the same six points, not a proper quotient.
    assert ask(quotient(target.point(six.gen(0))) == quotient.codomain().zero()) is False
    assert ask(quotient(target.point(2 * six.gen(0))) == quotient.codomain().zero()) is False
    assert ask(quotient(target.point(3 * six.gen(0))) == quotient.codomain().zero()) is False
    identity = coequalizer_mediator(quotient, abelian_homomorphism(target, target, lambda x: x))
    assert ask(identity * quotient == abelian_homomorphism(target, target, lambda x: x)) is True


test_coequalizer_of_zero_and_doubling_is_the_quotient_by_the_even_classes()
test_the_coequalizer_of_a_pair_that_is_already_equal_is_the_identity_on_the_target()
