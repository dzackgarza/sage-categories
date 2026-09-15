"""Owner-side reconstruction records for OSCAR realizations of commutative rings."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any, cast

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization,
    NativeMorphismRealizations,
    NativeObjectRealization,
    NativeObjectRealizations,
)
from sage_categories.engines.julia_bridge import OscarHandle
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.type_aliases import EqualityInput

if TYPE_CHECKING:
    from sage_categories.cat.functors import Functor

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


@dataclass(frozen=True, eq=False, slots=True)
class OscarRingConstruction:
    """The owned construction data selecting one OSCAR commutative-ring realization."""

    data: object


_objects: NativeObjectRealizations[object, OscarRingConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()


@dataclass(frozen=True, eq=False, slots=True)
class _OscarRingElementDatum:
    """One OSCAR ring element, compared by OSCAR inside its exact retained ring."""

    ring: OscarHandle
    native: OscarHandle

    def __eq__(self, other: EqualityInput) -> bool:
        if not isinstance(other, _OscarRingElementDatum) or self.ring is not other.ring:
            return False
        return _oscar_runtime().ring_equal(self.native, other.native)

    def __hash__(self) -> int:
        return hash(self.ring)


def _native_ring_element(datum: Any, ring: OscarHandle) -> OscarHandle:
    assert isinstance(datum, _OscarRingElementDatum) and datum.ring is ring
    return datum.native


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


class _OscarCommutativeRingOperations(Category):
    """OSCAR execution of ring-map operations when both endpoints retain OSCAR rings."""

    class ObjectType:
        pass

    class ElementType:
        pass

    class MorphismType:
        pass

    def structure_functors(self) -> tuple[Functor, ...]:
        from sage_categories.cat.functors import Fun

        declarations, _morphisms_module, structured = _ring_runtime_modules()
        owner = structured.Rings(declarations.Sets)
        return (Fun(owner, owner).one(),)

    def construct_identity(
        self,
        member_object: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        if not _objects.has(member_object):
            return Category.construct_identity(self, member_object)
        oscar = _oscar_runtime()
        native = oscar.ring_identity(oscar_object_handle(member_object))
        return reconstruct_oscar_morphism(member_object, member_object, native)

    def composite(
        self,
        second: MorphismCategory.ObjectType,
        first: MorphismCategory.ObjectType,
    ) -> MorphismCategory.ObjectType:
        if not (_morphisms.has(first) and _morphisms.has(second)):
            return Category.composite(self, second, first)
        oscar = _oscar_runtime()
        native = oscar.ring_compose(oscar_morphism_handle(second), oscar_morphism_handle(first))
        return reconstruct_oscar_morphism(first.domain(), second.codomain(), native)

    def _morphism_equality(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> bool | None:
        if not (_morphisms.has(first) and _morphisms.has(second)):
            return Category._morphism_equality(self, first, second)
        return _oscar_runtime().ring_map_equal(oscar_morphism_handle(first), oscar_morphism_handle(second))


@cache
def _install_oscar_ring_operations() -> None:
    from sage_categories.cat.functors import Cat

    Cat().implement(_OscarCommutativeRingOperations)


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
    datum = cast(Any, value).datum()
    assert isinstance(datum, _OscarRingElementDatum)
    return datum.native


def oscar_morphism_handle(value: MorphismCategory.ObjectType) -> OscarHandle:
    """Return the isolated-worker handle retained for one owned OSCAR ring map."""
    native = oscar_native_morphism(value).native
    assert isinstance(native, OscarHandle)
    return native


def reconstruct_oscar_element(
    ring: CategoryOfCategories.ElementType,
    native: OscarHandle,
) -> CategoryOfCategories.ElementType:
    """Reconstruct one OSCAR ring element as a point of its exact owned ring."""
    return cast(CategoryOfCategories.ElementType, cast(Any, ring).point(_OscarRingElementDatum(oscar_object_handle(ring), native)))


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

    _install_oscar_ring_operations()
    oscar = _oscar_runtime()
    declarations, _morphisms, _structured = _ring_runtime_modules()
    Sets = declarations.Sets
    carrier = Sets.from_membership(
        lambda element: true if isinstance(element, _OscarRingElementDatum) and element.ring is native and oscar.ring_contains(native, element.native) else false
    )
    ring = certified_commutative_ring(
        carrier,
        lambda pair: _OscarRingElementDatum(
            native,
            oscar.ring_add(
                _native_ring_element(pair[0], native),
                _native_ring_element(pair[1], native),
            ),
        ),
        lambda pair: _OscarRingElementDatum(
            native,
            oscar.ring_multiply(
                _native_ring_element(pair[0], native),
                _native_ring_element(pair[1], native),
            ),
        ),
        _OscarRingElementDatum(native, oscar.ring_zero(native)),
        _OscarRingElementDatum(native, oscar.ring_one(native)),
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
    carrier_map = morphisms.Mor(Sets)(source_carrier, target_carrier)(
        lambda element: _OscarRingElementDatum(
            target_native,
            oscar.map_apply(native, _native_ring_element(element, source_native)),
        )
    )
    arrow = rings.homomorphism(source, target, carrier_map)
    refine(arrow, _owner().morphism_category(1))
    retain_oscar_native_morphism(arrow, native)
    return cast(MorphismCategory.ObjectType, arrow)
