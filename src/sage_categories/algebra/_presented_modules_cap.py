"""Compatibility surface for the presented-module computation firewall."""

from sage_categories.algebra._firewall.presented_modules_cap import (
    PresentedModuleConstruction,
    has_presented_native_morphism,
    has_presented_native_object,
    presented_native_morphism,
    presented_native_object,
    retain_presented_native_morphism,
    retain_presented_native_object,
)

__all__ = [
    "PresentedModuleConstruction",
    "has_presented_native_morphism",
    "has_presented_native_object",
    "presented_native_morphism",
    "presented_native_object",
    "retain_presented_native_morphism",
    "retain_presented_native_object",
]
