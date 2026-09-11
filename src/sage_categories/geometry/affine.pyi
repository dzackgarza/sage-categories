import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from dataclasses import dataclass
from functools import cache
from sage_categories.algebra.commutative_rings import PrimeIdeal
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeObjectRealization
from sage_categories.geometry.sheaves import RingPresheaf
from typing import Any
__all__ = ['AffineSpectrumPoint', 'AffineOpenCategory', 'AffineOpen', 'AffineSchemesCategory', 'AffineSchemes', 'native_affine_scheme', 'native_affine_morphism', 'Spec', 'affine_structure_sheaf']

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
    native: object
    section_ring: CategoryOfCategories.ElementType
    ancestors: tuple[AffineOpenCategory.ObjectType, ...]
    restrictions: tuple[tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType], ...]

class AffineOpenCategory(Category[Any, Any]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: _AffineOpenData) -> None:
            ...

        def native(self) -> object:
            ...

        def section_ring(self) -> CategoryOfCategories.ElementType:
            ...

        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> AffineOpenCategory.ObjectType:
            ...

        def codomain(self) -> AffineOpenCategory.ObjectType:
            ...

    def __init__(self, scheme: AffineSchemesCategory.ObjectType) -> None:
        ...

    def scheme(self) -> AffineSchemesCategory.ObjectType:
        ...

    def root(self) -> AffineOpenCategory.ObjectType:
        ...

    def principal_open(self, parent: AffineOpenCategory.ObjectType, element: CategoryOfCategories.ElementType) -> AffineOpenCategory.ObjectType:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, *args: Any, **kwargs: Any) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, member_object: Any) -> Any:
        ...

    def composite(self, second: Any, first: Any) -> Any:
        ...
AffineOpen = AffineOpenCategory.ObjectType

class AffineSchemesCategory(Category[Any, Any]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, coordinate_ring: CategoryOfCategories.ElementType) -> None:
            ...

        def coordinate_ring(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, pullback: MorphismCategory.ObjectType) -> None:
            ...

        def pullback(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> AffineSchemesCategory.ObjectType:
            ...

        def codomain(self) -> AffineSchemesCategory.ObjectType:
            ...

    def from_native(self, coordinate_ring: CategoryOfCategories.ElementType, native: object) -> AffineSchemesCategory.ObjectType:
        ...

    def from_native_morphism(self, source: AffineSchemesCategory.ObjectType, target: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType, native: object) -> AffineSchemesCategory.MorphismType:
        ...

    def spectrum_point(self, scheme: AffineSchemesCategory.ObjectType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> AffineSpectrumPoint:
        ...

    def map_spectrum_point(self, mapping: AffineSchemesCategory.MorphismType, point: AffineSpectrumPoint) -> tuple[AffineSpectrumPoint, MorphismCategory.ObjectType]:
        ...

@cache
def AffineSchemes() -> AffineSchemesCategory:
    ...

def native_affine_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, AffineSchemeConstruction]:
    ...

def native_affine_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]:
    ...
Spec: Functor

def affine_structure_sheaf(scheme: AffineSchemesCategory.ObjectType) -> tuple[AffineOpenCategory, RingPresheaf]:
    ...
