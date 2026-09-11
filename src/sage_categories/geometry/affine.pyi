from dataclasses import dataclass
from functools import cache
from typing import Any

from _typeshed import Incomplete

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_element_handle as oscar_element_handle,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_morphism_handle as oscar_morphism_handle,
)
from sage_categories.algebra._commutative_rings_oscar import (
    oscar_object_handle as oscar_object_handle,
)
from sage_categories.algebra.commutative_rings import (
    PrimeIdeal as PrimeIdeal,
)
from sage_categories.algebra.commutative_rings import (
    induced_stalk_map_to as induced_stalk_map_to,
)
from sage_categories.algebra.commutative_rings import (
    localize_at_prime as localize_at_prime,
)
from sage_categories.algebra.commutative_rings import (
    prime_ideal as prime_ideal,
)
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.native import (
    NativeMorphismRealization as NativeMorphismRealization,
)
from sage_categories.cat.native import (
    NativeMorphismRealizations as NativeMorphismRealizations,
)
from sage_categories.cat.native import (
    NativeObjectRealization as NativeObjectRealization,
)
from sage_categories.cat.native import (
    NativeObjectRealizations as NativeObjectRealizations,
)
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.engines import oscar as oscar
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle
from sage_categories.geometry.sheaves import RingPresheaf as RingPresheaf
from sage_categories.geometry.sheaves import ring_presheaf_from_functor as ring_presheaf_from_functor

__all__ = [
    "AffineOpen",
    "AffineOpenCategory",
    "AffineSchemes",
    "AffineSchemesCategory",
    "AffineSpectrumPoint",
    "Spec",
    "affine_structure_sheaf",
    "native_affine_morphism",
    "native_affine_scheme",
]

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

class _StaticRoles_AffineOpenCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _AffineOpenData) -> None: ...
        def native(self) -> OscarHandle: ...
        def section_ring(self) -> CategoryOfCategories.ElementType: ...
        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        ...

        def domain(self) -> AffineOpenCategory.ObjectType: ...
        def codomain(self) -> AffineOpenCategory.ObjectType: ...

class AffineOpenCategory(
    _StaticRoles_AffineOpenCategory,
    Category[Any, Any, _StaticRoles_AffineOpenCategory.ObjectType, _StaticRoles_AffineOpenCategory.ElementType, _StaticRoles_AffineOpenCategory.MorphismType],
):
    def __init__(self, scheme: AffineSchemesCategory.ObjectType) -> None: ...
    def scheme(self) -> AffineSchemesCategory.ObjectType: ...
    def root(self) -> AffineOpenCategory.ObjectType: ...
    def principal_open(self, parent: AffineOpenCategory.ObjectType, element: CategoryOfCategories.ElementType) -> AffineOpenCategory.ObjectType: ...
    def construct_morphism(
        self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, *args: Any, **kwargs: Any
    ) -> MorphismCategory.ObjectType: ...
    def construct_identity(self, member_object: Any) -> Any: ...
    def composite(self, second: Any, first: Any) -> Any: ...

AffineOpen: Incomplete

class _StaticRoles_AffineSchemesCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, coordinate_ring: CategoryOfCategories.ElementType) -> None: ...
        def coordinate_ring(self) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, pullback: MorphismCategory.ObjectType) -> None: ...
        def pullback(self) -> MorphismCategory.ObjectType: ...
        def domain(self) -> AffineSchemesCategory.ObjectType: ...
        def codomain(self) -> AffineSchemesCategory.ObjectType: ...

class AffineSchemesCategory(
    _StaticRoles_AffineSchemesCategory,
    Category[Any, Any, _StaticRoles_AffineSchemesCategory.ObjectType, _StaticRoles_AffineSchemesCategory.ElementType, _StaticRoles_AffineSchemesCategory.MorphismType],
):
    def from_native(self, coordinate_ring: CategoryOfCategories.ElementType, native: OscarHandle) -> AffineSchemesCategory.ObjectType: ...
    def from_native_morphism(
        self, source: AffineSchemesCategory.ObjectType, target: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType, native: OscarHandle
    ) -> AffineSchemesCategory.MorphismType: ...
    def spectrum_point(self, scheme: AffineSchemesCategory.ObjectType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> AffineSpectrumPoint: ...
    def map_spectrum_point(self, mapping: AffineSchemesCategory.MorphismType, point: AffineSpectrumPoint) -> tuple[AffineSpectrumPoint, MorphismCategory.ObjectType]: ...

@cache
def AffineSchemes() -> AffineSchemesCategory: ...
def native_affine_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[OscarHandle, AffineSchemeConstruction]: ...
def native_affine_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[OscarHandle]: ...

Spec: Functor

def affine_structure_sheaf(scheme: AffineSchemesCategory.ObjectType) -> tuple[AffineOpenCategory, RingPresheaf]: ...
