import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from dataclasses import dataclass
from functools import cache
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.native import NativeMorphismRealization, NativeObjectRealization
from sage_categories.geometry.affine import AffineOpenCategory, AffineSchemesCategory
from sage_categories.geometry.sheaves import RingPresheaf
from typing import Any
__all__ = ['TwoChartGluing', 'ProjectiveLinePresentation', 'SchemesCategory', 'Schemes', 'native_scheme', 'native_scheme_morphism', 'projective_line']

@dataclass(frozen=True, eq=False, slots=True)
class _AffineSchemeConstruction:
    affine: AffineSchemesCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class TwoChartGluing:
    left: AffineSchemesCategory.ObjectType
    right: AffineSchemesCategory.ObjectType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_to_right_pullback: MorphismCategory.ObjectType
    right_to_left_pullback: MorphismCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveLinePresentation:
    scheme: SchemesCategory.ObjectType
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: SchemesCategory.MorphismType
    right_inclusion: SchemesCategory.MorphismType
    chart_swap: SchemesCategory.MorphismType
    structure_sheaf: RingPresheaf
    overlap_swap: MorphismCategory.ObjectType

class SchemesCategory(Category[Any, Any]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, construction: object) -> None:
            ...

        def construction(self) -> object:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> SchemesCategory.ObjectType:
            ...

        def codomain(self) -> SchemesCategory.ObjectType:
            ...

    def __init__(self) -> None:
        ...

    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType:
        ...

    def glue_two_affines(self, left: AffineSchemesCategory.ObjectType, right: AffineSchemesCategory.ObjectType, left_open: AffineOpenCategory.ObjectType, right_open: AffineOpenCategory.ObjectType, left_to_right_pullback: MorphismCategory.ObjectType, right_to_left_pullback: MorphismCategory.ObjectType) -> tuple[SchemesCategory.ObjectType, SchemesCategory.MorphismType, SchemesCategory.MorphismType]:
        ...

    def gluing_mediator(self, glued: SchemesCategory.ObjectType, target: SchemesCategory.ObjectType, left_map: SchemesCategory.MorphismType, right_map: SchemesCategory.MorphismType) -> SchemesCategory.MorphismType:
        ...

    def chart_map(self, source: AffineSchemesCategory.ObjectType, target: SchemesCategory.ObjectType, target_chart: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType) -> SchemesCategory.MorphismType:
        ...

@cache
def Schemes() -> SchemesCategory:
    ...

def native_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[object, object]:
    ...

def native_scheme_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[object]:
    ...

def projective_line(field: CategoryOfCategories.ElementType) -> ProjectiveLinePresentation:
    ...
