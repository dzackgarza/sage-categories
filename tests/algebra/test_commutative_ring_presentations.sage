"""Owned OSCAR polynomial, quotient, and principal-localization presentations."""

from sage_categories.algebra import (
    induced_stalk_map,
    inverse_unit,
    localization_extension,
    localize_at_prime,
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
    prime_ideal,
    principal_localization,
    quotient_ring,
)
from sage_categories.algebra.commutative_rings import (
    prime_contains,
    prime_ideal_extension,
)
from sage_categories.all import Mor, ask
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

    target, (_u,) = polynomial_ring(field, ("u",))
    quotient_map = presented_ring_homomorphism(dual_numbers, target, (target.zero(),))
    assert quotient_map.domain() is dual_numbers and quotient_map.codomain() is target
    assert ask(quotient_map(epsilon) == target.zero()) is True



def test_prime_localizations_and_stalk_map_retain_owned_endpoints() -> None:
    field = prime_field(5)
    source, (_t,) = polynomial_ring(field, ("t",))
    target, (u,) = polynomial_ring(field, ("u",))
    mapping = presented_ring_homomorphism(source, target, (u,))
    target_prime = prime_ideal(target, (u,))
    assert prime_contains(target_prime, u) is True
    assert prime_contains(target_prime, target.one()) is False
    extended_source_prime = prime_ideal_extension(mapping, prime_ideal(source, (_t,)))
    assert prime_contains(extended_source_prime, u) is True
    target_local, target_localization = localize_at_prime(target_prime)
    source_prime, source_local, induced_target_local, stalk = induced_stalk_map(
        mapping, target_prime
    )

    assert source_prime.ring is source
    assert target_localization.domain() is target
    assert target_localization.codomain() is target_local
    assert induced_target_local is not target_local
    assert stalk.domain() is source_local
    assert stalk.codomain() is induced_target_local


test_polynomial_quotient_and_principal_localization_maps()
test_prime_localizations_and_stalk_map_retain_owned_endpoints()
