"""Compatibility surface for the finite-set computation firewall."""

from sage_categories.sets._firewall.finite_cap import (
    FiniteIndexing,
    finite_native_morphism,
    finite_native_object,
    has_finite_native_morphism,
    has_finite_native_object,
    retain_finite_native_morphism,
    retain_finite_native_object,
)

__all__ = [
    "FiniteIndexing",
    "finite_native_morphism",
    "finite_native_object",
    "has_finite_native_morphism",
    "has_finite_native_object",
    "retain_finite_native_morphism",
    "retain_finite_native_object",
]
