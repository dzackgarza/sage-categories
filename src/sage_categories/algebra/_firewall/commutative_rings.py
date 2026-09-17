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
from sage_categories.cat.predicates import assume
from sage_categories.engines.julia_bridge import OscarHandle

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


@dataclass(frozen=True, eq=False, slots=True)
class _PrincipalLocalizationConstruction:
    source: CategoryOfCategories.ElementType
    element: CategoryOfCategories.ElementType


_objects: NativeObjectRealizations[object, OscarRingConstruction] = NativeObjectRealizations()
_morphisms: NativeMorphismRealizations[object] = NativeMorphismRealizations()
_prime_ideals: dict[object, OscarHandle] = {}


@dataclass(frozen=True, eq=False, slots=True)
class _OscarRingElementDatum:
    """One OSCAR ring element, compared by OSCAR inside its exact retained ring."""

    ring: OscarHandle
    native: OscarHandle

    def __eq__(self, other: object) -> bool:
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

        owner = _owner()
        return (Fun(owner, owner).one(),)

    def _morphism_equality(
        self,
        first: MorphismCategory.ObjectType,
        second: MorphismCategory.ObjectType,
    ) -> bool | None:
        if not (_morphisms.has(first) and _morphisms.has(second)):
            return None
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
    if not _morphisms.has(value):
        oscar_morphism_handle(value)
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
    """Return or lazily assemble the OSCAR map for one owned ring morphism.

    Categorical identity/composition stays Cat-owned.  The firewall lowers Cat's
    retained formal identity/composite data only when an OSCAR consumer actually asks
    for a native map.
    """
    if not _morphisms.has(value):
        oscar = _oscar_runtime()
        word = value.word()
        if not word:
            native = oscar.ring_identity(oscar_object_handle(value.domain()))
        elif value.is_composite():
            first, second = value.factors()
            native = oscar.ring_compose(oscar_morphism_handle(second), oscar_morphism_handle(first))
        else:
            raise AssertionError(f"{value!r} has no OSCAR realization")
        retain_oscar_native_morphism(value, native)
    native = _morphisms.realization(value).native
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

    from sage_categories.algebra._certified_commutative_ring import (
        certified_commutative_ring,
    )

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
    assume(_owner().morphism_category(1).membership_proposition(arrow))
    retain_oscar_native_morphism(arrow, native)
    return cast(MorphismCategory.ObjectType, arrow)


def construction(value: CategoryOfCategories.ElementType) -> object:
    """Return the owned construction datum attached to an OSCAR-backed ring."""
    record = oscar_native_object(value)
    assert isinstance(record.construction, OscarRingConstruction)
    return record.construction.data


def integer_ring(construction_data: object) -> CategoryOfCategories.ElementType:
    native = _oscar_runtime().integer_ring()
    return reconstruct_oscar_object(native, construction_data)


def prime_field(characteristic: int, construction_data: object) -> CategoryOfCategories.ElementType:
    native = _oscar_runtime().prime_field(characteristic)
    return reconstruct_oscar_object(native, construction_data)


def polynomial_ring(
    base: CategoryOfCategories.ElementType,
    names: tuple[str, ...],
    construction_data: object,
) -> tuple[CategoryOfCategories.ElementType, tuple[CategoryOfCategories.ElementType, ...]]:
    native, generators = _oscar_runtime().polynomial_ring(oscar_object_handle(base), names)
    ring = reconstruct_oscar_object(native, construction_data)
    return ring, tuple(reconstruct_oscar_element(ring, generator) for generator in generators)


def quotient_ring(
    source: CategoryOfCategories.ElementType,
    relations: tuple[CategoryOfCategories.ElementType, ...],
    construction_data: object,
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    native_ring, native_map = _oscar_runtime().quotient(
        oscar_object_handle(source),
        tuple(oscar_element_handle(relation) for relation in relations),
    )
    target = reconstruct_oscar_object(native_ring, construction_data)
    return target, reconstruct_oscar_morphism(source, target, native_map)


def polynomial_coefficient_map(
    base: CategoryOfCategories.ElementType,
    polynomial: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    native = _oscar_runtime().polynomial_coefficient_map(
        oscar_object_handle(base), oscar_object_handle(polynomial)
    )
    return reconstruct_oscar_morphism(base, polynomial, native)


def principal_localization(
    source: CategoryOfCategories.ElementType,
    element: CategoryOfCategories.ElementType,
    construction_data: object,
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    native_ring, native_map = _oscar_runtime().localization_at_element(
        oscar_object_handle(source),
        oscar_element_handle(element),
    )
    target = reconstruct_oscar_object(native_ring, construction_data)
    return target, reconstruct_oscar_morphism(source, target, native_map)


def retain_prime_ideal(
    value: object,
    ring: CategoryOfCategories.ElementType,
    generators: tuple[CategoryOfCategories.ElementType, ...],
) -> None:
    _prime_ideals[value] = _oscar_runtime().prime_ideal(
        oscar_object_handle(ring),
        tuple(oscar_element_handle(generator) for generator in generators),
    )


def _prime_ideal_handle(value: object) -> OscarHandle:
    assert value in _prime_ideals, f"{value!r} has no OSCAR prime-ideal realization"
    return _prime_ideals[value]


def prime_ideal_generators(value: object) -> tuple[CategoryOfCategories.ElementType, ...]:
    """Reconstruct the native generators of one retained prime in its exact owned ring."""
    ring = cast(Any, value).ring
    return tuple(
        reconstruct_oscar_element(ring, generator)
        for generator in _oscar_runtime().ideal_generators(_prime_ideal_handle(value))
    )


def prime_ideal_contains(
    value: object,
    element: CategoryOfCategories.ElementType,
) -> bool:
    """Decide ideal membership at the private OSCAR boundary."""
    return _oscar_runtime().ideal_contains(
        _prime_ideal_handle(value),
        oscar_element_handle(element),
    )


def retain_prime_ideal_preimage(
    value: object,
    mapping: MorphismCategory.ObjectType,
    target_prime: object,
) -> None:
    _prime_ideals[value] = _oscar_runtime().prime_ideal_preimage(
        oscar_morphism_handle(mapping),
        _prime_ideal_handle(target_prime),
    )


def retain_prime_ideal_extension(
    value: object,
    mapping: MorphismCategory.ObjectType,
    source_prime: object,
) -> None:
    _prime_ideals[value] = _oscar_runtime().prime_ideal_extension(
        oscar_morphism_handle(mapping),
        _prime_ideal_handle(source_prime),
    )


def localization_at_prime(
    ring: CategoryOfCategories.ElementType,
    prime: object,
    construction_data: object,
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    native_ring, native_map = _oscar_runtime().localization_at_prime(
        oscar_object_handle(ring),
        _prime_ideal_handle(prime),
    )
    target = reconstruct_oscar_object(native_ring, construction_data)
    return target, reconstruct_oscar_morphism(ring, target, native_map)


def stalk_map(
    mapping: MorphismCategory.ObjectType,
    source_localized: CategoryOfCategories.ElementType,
    target_localized: CategoryOfCategories.ElementType,
    target_localization: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    native = _oscar_runtime().stalk_map(
        oscar_morphism_handle(mapping),
        oscar_object_handle(source_localized),
        oscar_object_handle(target_localized),
        oscar_morphism_handle(target_localization),
    )
    return reconstruct_oscar_morphism(source_localized, target_localized, native)


def presented_ring_homomorphism(
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    generator_images: tuple[CategoryOfCategories.ElementType, ...],
) -> MorphismCategory.ObjectType:
    native = _oscar_runtime().hom(
        oscar_object_handle(source),
        oscar_object_handle(target),
        tuple(oscar_element_handle(image) for image in generator_images),
    )
    return reconstruct_oscar_morphism(source, target, native)


def localization_extension(
    localized: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
    base_map: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    construction_data = construction(localized)
    assert getattr(construction_data, "source", None) is base_map.domain()
    assert base_map.codomain() is target
    native = _oscar_runtime().localization_hom(
        oscar_object_handle(localized),
        oscar_object_handle(target),
        oscar_morphism_handle(base_map),
    )
    return reconstruct_oscar_morphism(localized, target, native)


def inverse_unit(element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    return reconstruct_oscar_element(element.parent(), _oscar_runtime().ring_inverse(oscar_element_handle(element)))


def principal_localization_from_native(
    source: CategoryOfCategories.ElementType,
    element: CategoryOfCategories.ElementType,
    native_localized: object,
    native_map: object,
    construction_data: object | None = None,
) -> tuple[CategoryOfCategories.ElementType, MorphismCategory.ObjectType]:
    assert isinstance(native_localized, OscarHandle) and isinstance(native_map, OscarHandle)
    if construction_data is None:
        construction_data = _PrincipalLocalizationConstruction(source, element)
    localized = reconstruct_oscar_object(native_localized, construction_data)
    return localized, reconstruct_oscar_morphism(source, localized, native_map)
