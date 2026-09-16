"""Compatibility surface for the commutative-ring computation firewall.

Theory modules use :mod:`sage_categories.algebra._firewall.commutative_rings` directly.
This module preserves the older reconstruction names for consumers while containing no
backend or runtime state of its own.
"""

from sage_categories.algebra._firewall.commutative_rings import (
    OscarRingConstruction,
    oscar_element_handle,
    oscar_morphism_handle,
    oscar_native_morphism,
    oscar_native_object,
    oscar_object_handle,
    reconstruct_oscar_element,
    reconstruct_oscar_morphism,
    reconstruct_oscar_object,
    retain_oscar_native_morphism,
    retain_oscar_native_object,
)

__all__ = [
    "OscarRingConstruction",
    "oscar_element_handle",
    "oscar_morphism_handle",
    "oscar_native_morphism",
    "oscar_native_object",
    "oscar_object_handle",
    "reconstruct_oscar_element",
    "reconstruct_oscar_morphism",
    "reconstruct_oscar_object",
    "retain_oscar_native_morphism",
    "retain_oscar_native_object",
]
