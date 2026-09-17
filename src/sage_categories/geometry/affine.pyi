from _typeshed import Incomplete
from dataclasses import dataclass
from functools import cache
from sage_categories.algebra._commutative_rings_oscar import oscar_element_handle as oscar_element_handle, oscar_morphism_handle as oscar_morphism_handle, oscar_object_handle as oscar_object_handle
from sage_categories.algebra.commutative_rings import PrimeIdeal as PrimeIdeal, induced_stalk_map_to as induced_stalk_map_to, localize_at_prime as localize_at_prime, prime_ideal as prime_ideal
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization as NativeMorphismRealization, NativeMorphismRealizations as NativeMorphismRealizations, NativeObjectRealization as NativeObjectRealization, NativeObjectRealizations as NativeObjectRealizations
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.engines import oscar as oscar
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle
from sage_categories.geometry.sheaves import RingPresheaf as RingPresheaf, ring_presheaf_from_functor as ring_presheaf_from_functor
from typing import Any

@dataclass(frozen=True, eq=False, slots=True)
class AffineSchemeConstruction:
    coordinate_ring: CategoryOfCategories.ElementType

@dataclass(frozen=True, eq=False, slots=True)
class AffineSpectrumPoint:
    scheme: AffineSchemesCategory.ObjectType
    prime: PrimeIdeal
    local_ring: CategoryOfCategories.ElementType
    localization: MorphismCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class _AffineOpenData:
    scheme: AffineSchemesCategory.ObjectType
    native: OscarHandle
    section_ring: CategoryOfCategories.ElementType
    ancestors: tuple[AffineOpenCategory.ObjectType, ...]
    restrictions: tuple[tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType], ...]

class AffineOpenCategory(Category[Any, Any]):

    class ObjectType:

        def __init__(self, data: _AffineOpenData) -> None:
            ...

        def native(self) -> OscarHandle:
            ...

        def section_ring(self) -> CategoryOfCategories.ElementType:
            ...

        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, scheme: AffineSchemesCategory.ObjectType) -> None:
        ...

    def scheme(self) -> AffineSchemesCategory.ObjectType:
        ...

    def root(self) -> AffineOpenCategory.ObjectType:
        ...

    def principal_open(self, parent: AffineOpenCategory.ObjectType, element: CategoryOfCategories.ElementType) -> AffineOpenCategory.ObjectType:
        ...

    def construct_morphism(self, domain: AffineOpenCategory.ObjectType, codomain: AffineOpenCategory.ObjectType, *args: Any, **kwargs: Any) -> AffineOpenCategory.MorphismType:
        ...

    def construct_identity(self, member_object: AffineOpenCategory.ObjectType) -> AffineOpenCategory.MorphismType:
        ...

    def composite(self, second: AffineOpenCategory.MorphismType, first: AffineOpenCategory.MorphismType) -> AffineOpenCategory.MorphismType:
        ...
AffineOpen: Incomplete

class AffineSchemesCategory(Category[Any, Any]):

    class ObjectType:

        def __init__(self, coordinate_ring: CategoryOfCategories.ElementType) -> None:
            ...

        def coordinate_ring(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType:
        ...

    class MorphismType:

        def __init__(self, pullback: MorphismCategory.ObjectType) -> None:
            ...

        def pullback(self) -> MorphismCategory.ObjectType:
            ...

    def from_native(self, coordinate_ring: CategoryOfCategories.ElementType, native: OscarHandle) -> AffineSchemesCategory.ObjectType:
        ...

    def from_native_morphism(self, source: AffineSchemesCategory.ObjectType, target: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType, native: OscarHandle) -> AffineSchemesCategory.MorphismType:
        ...

    def spectrum_point(self, scheme: AffineSchemesCategory.ObjectType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> AffineSpectrumPoint:
        ...

    def map_spectrum_point(self, mapping: AffineSchemesCategory.MorphismType, point: AffineSpectrumPoint) -> tuple[AffineSpectrumPoint, MorphismCategory.ObjectType]:
        ...

@cache
def AffineSchemes() -> AffineSchemesCategory:
    ...

def native_affine_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[OscarHandle, AffineSchemeConstruction]:
    ...

def native_affine_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[OscarHandle]:
    ...
Spec: Functor

def affine_structure_sheaf(scheme: AffineSchemesCategory.ObjectType) -> tuple[AffineOpenCategory, RingPresheaf[AffineOpenCategory.ObjectType]]:
    ...
