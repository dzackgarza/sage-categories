"""Owned OSCAR polynomial, quotient, and principal-localization presentations."""

from sage_categories.all import Mor, ask
from sage_categories.algebra import (
    inverse_unit,
    localization_extension,
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
    principal_localization,
    quotient_ring,
)
from sage_categories.cat.structured_objects import Rings
from sage_categories.sets.finite import Sets


def test_polynomial_quotient_and_principal_localization_maps() -> None:
    field = prime_field(5)
    polynomial, (t,) = polynomial_ring(field, ("t",))
    rings = Rings(Sets)
    assert field in rings.Commutative() and polynomial in rings.Commutative()

    localized, localization_map = principal_localization(polynomial, t)
    assert localization_map.domain() is polynomial and localization_map.codomain() is localized
    localized_t = localization_map(t)
    inverse_t = inverse_unit(localized_t)
    assert ask(localized_t * inverse_t == localized.one()) is True

    extension = localization_extension(localized, localized, localization_map)
    assert extension.domain() is localized and extension.codomain() is localized
    assert ask(extension * localization_map == localization_map) is True
    assert ask(extension == Mor(rings)(localized, localized).one()) is True

    dual_numbers, projection = quotient_ring(polynomial, (t * t,))
    epsilon = projection(t)
    assert projection.domain() is polynomial and projection.codomain() is dual_numbers
    assert ask(epsilon == dual_numbers.zero()) is False
    assert ask(epsilon * epsilon == dual_numbers.zero()) is True

    target, (u,) = polynomial_ring(field, ("u",))
    quotient_map = presented_ring_homomorphism(dual_numbers, target, (target.zero(),))
    assert quotient_map.domain() is dual_numbers and quotient_map.codomain() is target
    assert ask(quotient_map(epsilon) == target.zero()) is True


test_polynomial_quotient_and_principal_localization_maps()
