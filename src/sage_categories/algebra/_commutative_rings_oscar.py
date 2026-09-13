"""Owner-side reconstruction records for OSCAR realizations of commutative rings."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import Any, cast

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.engines.julia_bridge import OscarHandle

__all__ = [
    "OscarRingConstruction",
    "oscar_element_handle",
    "oscar_morphism_handle",
    "oscar_native_morphism",
    "oscar_native_object",
    "oscar_object_handle",
    "reconstruct_oscar_morphism",
    "reconstruct_oscar_object",
    "retain_oscar_native_morphism",
    "retain_oscar_native_object",
]


@dataclass(frozen=True, eq=False, slots=True)
class OscarRingConstruction:
    """The owned construction data selecting one OSCAR commutative-ring realization."""

    data: object


_objects: NativeObjectRealizations[object, OscarRingConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


def _ring_runtime_modules() -> tuple[ModuleType, ModuleType, ModuleType]:
    """Load the declaration, morphism, and structured-object owners at the cycle-safe OSCAR boundary."""
    return (
        import_module("sage_categories.cat.declarations"),
        import_module("sage_categories.cat.morphisms"),
        import_module("sage_categories.cat.structured_objects"),
    )


def _oscar_runtime() -> ModuleType:
    """Load the OSCAR execution adapter at the one cycle-safe reconstruction boundary."""
    from sage_categories.engines import oscar

    return oscar


def _owner() -> Any:
    declarations, _morphisms_module, structured = _ring_runtime_modules()
    return structured.Rings(declarations.Sets).Commutative()


def retain_oscar_native_object(
    value: CategoryOfCategories.ElementType,
    native: object,
    construction: object,
) -> NativeObjectRealization[object, OscarRingConstruction]:
    """Retain one native ring against its exact owned commutative-ring object."""
    return _objects.retain(_owner(), value, native, OscarRingConstruction(construction))


def oscar_native_object(
    value: CategoryOfCategories.ElementType,
) -> NativeObjectRealization[object, OscarRingConstruction]:
    return _objects.realization(value)


def retain_oscar_native_morphism(value: MorphismCategory.ObjectType, native: object) -> NativeMorphismRealization[object]:
    """Retain one native ring map with the exact owned source and target rings."""
    return _morphisms.retain(_owner(), value, value.domain(), value.codomain(), native)


def oscar_native_morphism(
    value: MorphismCategory.ObjectType,
) -> NativeMorphismRealization[object]:
    return _morphisms.realization(value)


def oscar_object_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    """Return the isolated-worker handle retained for one owned OSCAR ring."""
    native = oscar_native_object(value).native
    assert isinstance(native, OscarHandle)
    return native


def oscar_element_handle(value: CategoryOfCategories.ElementType) -> OscarHandle:
    """Return the isolated-worker handle stored as one OSCAR ring element datum."""
    native = cast(Any, value).datum()
    assert isinstance(native, OscarHandle)
    return native


def oscar_morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle:
    """Return the isolated-worker handle retained for one owned OSCAR ring map."""
    native = oscar_native_morphism(value).native
    assert isinstance(native, OscarHandle)
    return native


def reconstruct_oscar_object(
    native: OscarHandle,
    construction: object,
) -> CategoryOfCategories.ElementType:
    """Reconstruct an OSCAR-certified commutative ring in the existing ``Rings(Sets)`` owner.

    OSCAR owns the ring laws and evaluates the primitive operations.  Reconstruction
    builds the existing named monoid data and records the native certification by
    refinement into the corresponding law subcategories; it does not reimplement or
    numerically sample any ring law.
    """
    from sympy import false, true

    from sage_categories.algebra._certified_commutative_ring import certified_commutative_ring

    oscar = _oscar_runtime()
    declarations, _morphisms, _structured = _ring_runtime_modules()
    Sets = declarations.Sets
    carrier = Sets.from_membership(lambda element: true if oscar.ring_contains(native, element) else false)
    ring = certified_commutative_ring(
        carrier,
        lambda pair: oscar.ring_add(pair[0], pair[1]),
        lambda pair: oscar.ring_multiply(pair[0], pair[1]),
        oscar.ring_zero(native),
        oscar.ring_one(native),
    )
    retain_oscar_native_object(ring, native, construction)
    return cast(CategoryOfCategories.ElementType, ring)


def reconstruct_oscar_morphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    native: OscarHandle,
) -> MorphismCategory.ObjectType:
    """Reconstruct an OSCAR-certified ring map with the exact owned endpoints."""
    oscar = _oscar_runtime()
    source_native = oscar_object_handle(source)
    target_native = oscar_object_handle(target)
    assert oscar.same_native(oscar.domain(native), source_native)
    assert oscar.same_native(oscar.codomain(native), target_native)
    declarations, morphisms, structured = _ring_runtime_modules()
    Sets = declarations.Sets
    rings = structured.Rings(Sets)
    forgetful = rings.forgetful()
    source_carrier = forgetful.on_object(source)
    target_carrier = forgetful.on_object(target)
    carrier_map = morphisms.Mor(Sets)(source_carrier, target_carrier)(lambda element: oscar.map_apply(native, element))
    arrow = rings.homomorphism(source, target, carrier_map)
    retain_oscar_native_morphism(arrow, native)
    return cast(MorphismCategory.ObjectType, arrow)
