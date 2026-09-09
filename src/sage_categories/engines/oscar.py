"""Pinned OSCAR operations allocated to commutative rings and affine geometry."""

from __future__ import annotations

from sage_categories.engines.julia_bridge import oscar_bridge as bridge

__all__ = [
    "codomain",
    "domain",
    "generators",
    "hom",
    "localization_at_element",
    "localization_hom",
    "map_apply",
    "polynomial_ring",
    "prime_field",
    "quotient",
    "ring_add",
    "ring_coerce",
    "ring_contains",
    "ring_multiply",
    "ring_negate",
    "ring_one",
    "ring_zero",
    "same_native",
]


def prime_field(characteristic: int) -> object:
    """Return OSCAR's prime field ``GF(characteristic)``."""
    return bridge().prime_field(characteristic)


def polynomial_ring(base: object, names: tuple[str, ...]) -> tuple[object, tuple[object, ...]]:
    """Return OSCAR's multivariate polynomial ring and its ordered generators."""
    ring, generators = bridge().polynomial_ring_with_generators(base, list(names))
    return ring, tuple(generators)


def quotient(ring: object, relations: tuple[object, ...]) -> tuple[object, object]:
    """Return ``ring/(relations)`` and its canonical projection."""
    quotient_ring, projection = bridge().quotient_ring(ring, list(relations))
    return quotient_ring, projection


def localization_at_element(ring: object, element: object) -> tuple[object, object]:
    """Return the principal localization ``ring[element^-1]`` and its canonical map."""
    localized, canonical = bridge().localization_at_element(ring, element)
    return localized, canonical


def hom(source: object, target: object, images: tuple[object, ...]) -> object:
    """Return the OSCAR ring homomorphism defined by generator images."""
    return bridge().ring_hom(source, target, list(images))


def localization_hom(localized: object, target: object, base_map: object) -> object:
    """Extend ``base_map`` uniquely across a principal localization."""
    return bridge().localization_hom(localized, target, base_map)


def map_apply(mapping: object, element: object) -> object:
    return bridge().map_apply(mapping, element)


def domain(mapping: object) -> object:
    return bridge().map_domain(mapping)


def codomain(mapping: object) -> object:
    return bridge().map_codomain(mapping)


def generators(ring: object) -> tuple[object, ...]:
    return tuple(bridge().ring_generators(ring))


def ring_contains(ring: object, element: object) -> bool:
    return bool(bridge().ring_contains(ring, element))


def ring_zero(ring: object) -> object:
    return bridge().ring_zero(ring)


def ring_one(ring: object) -> object:
    return bridge().ring_one(ring)


def ring_add(first: object, second: object) -> object:
    return bridge().ring_add(first, second)


def ring_multiply(first: object, second: object) -> object:
    return bridge().ring_multiply(first, second)


def ring_negate(element: object) -> object:
    return bridge().ring_negate(element)


def ring_coerce(ring: object, value: object) -> object:
    return bridge().ring_coerce(ring, value)


def same_native(first: object, second: object) -> bool:
    return bool(bridge().same_native(first, second))
