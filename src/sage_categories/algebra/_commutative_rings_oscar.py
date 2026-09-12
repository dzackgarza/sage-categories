"""Owner-side reconstruction records for OSCAR realizations of commutative rings."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
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


def _owner() -> Any:
    structured_objects = import_module("sage_categories.cat.structured_objects")
    declarations = import_module("sage_categories.cat.declarations")
    return structured_objects.Rings(declarations.Sets).Commutative()


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

    from sage_categories.engines import oscar

    calculus = import_module("sage_categories.cat.calculus")
    declarations = import_module("sage_categories.cat.declarations")
    monoidal_module = import_module("sage_categories.cat.monoidal")
    morphisms = import_module("sage_categories.cat.morphisms")
    refinement = import_module("sage_categories.kernel.refinement")
    structured = import_module("sage_categories.cat.structured_objects")
    Sets = declarations.Sets
    Mor = morphisms.Mor
    monoidal = monoidal_module.Cartesian(Sets)
    carrier = Sets.from_membership(lambda element: true if oscar.ring_contains(native, element) else false)
    product = calculus.binary_product_data(Sets, carrier, carrier).apex()
    addition = Mor(Sets)(product, carrier)(lambda pair: oscar.ring_add(pair[0], pair[1]))
    multiplication = Mor(Sets)(product, carrier)(lambda pair: oscar.ring_multiply(pair[0], pair[1]))
    zero = Mor(Sets)(monoidal.unit(), carrier)(lambda _: oscar.ring_zero(native))
    one = Mor(Sets)(monoidal.unit(), carrier)(lambda _: oscar.ring_one(native))

    magmas = structured.Magmas(monoidal)
    pointed_magmas = structured.PointedMagmas(monoidal.tensor(), monoidal.unit())
    monoids = structured.Monoids(monoidal)

    def certified_monoid(
        operation: MorphismCategory.ObjectType,
        unit: MorphismCategory.ObjectType,
    ) -> CategoryOfCategories.ElementType:
        magma = magmas.algebra(carrier, operation)
        pointed = pointed_magmas.algebra(magma, unit)
        refinement.refine(pointed, monoids)
        return cast(CategoryOfCategories.ElementType, pointed)

    additive_monoid = certified_monoid(addition, zero)
    refinement.refine(additive_monoid, structured.Groups(monoidal))
    additive_monoids = structured.AdditiveMonoids(monoidal)
    additive = additive_monoids.renamed(additive_monoid)
    refinement.refine(additive, additive_monoids.Commutative())
    additive_groups = structured.AdditiveGroups(monoidal)
    group = additive_groups.renamed(additive_monoid)
    refinement.refine(group, additive_groups.Commutative())

    multiplicative_monoid = certified_monoid(multiplication, one)
    multiplicative = structured.MultiplicativeMonoids(monoidal).renamed(multiplicative_monoid)

    semirings = structured.Semirings(Sets)
    pair = semirings._pairs((additive, multiplicative, carrier))
    refinement.refine(pair, semirings)
    rings = structured.Rings(Sets)
    ring = rings._ring(pair, group, additive)
    refinement.refine(ring, rings.Commutative())
    retain_oscar_native_object(ring, native, construction)
    return cast(CategoryOfCategories.ElementType, ring)


def reconstruct_oscar_morphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    native: OscarHandle,
) -> MorphismCategory.ObjectType:
    """Reconstruct an OSCAR-certified ring map with the exact owned endpoints."""
    from sage_categories.engines import oscar

    source_native = oscar_object_handle(source)
    target_native = oscar_object_handle(target)
    assert oscar.same_native(oscar.domain(native), source_native)
    assert oscar.same_native(oscar.codomain(native), target_native)
    declarations = import_module("sage_categories.cat.declarations")
    morphisms = import_module("sage_categories.cat.morphisms")
    structured = import_module("sage_categories.cat.structured_objects")
    Sets = declarations.Sets
    rings = structured.Rings(Sets)
    forgetful = rings.forgetful()
    source_carrier = forgetful.on_object(source)
    target_carrier = forgetful.on_object(target)
    carrier_map = morphisms.Mor(Sets)(source_carrier, target_carrier)(lambda element: oscar.map_apply(native, element))
    arrow = rings.homomorphism(source, target, carrier_map)
    retain_oscar_native_morphism(arrow, native)
    return cast(MorphismCategory.ObjectType, arrow)
