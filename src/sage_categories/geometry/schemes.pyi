from dataclasses import dataclass
from functools import cache
from typing import Any

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.algebra._commutative_rings_oscar import oscar_morphism_handle as oscar_morphism_handle
from sage_categories.algebra.commutative_rings import (
    inverse_unit as inverse_unit,
)
from sage_categories.algebra.commutative_rings import (
    localization_extension as localization_extension,
)
from sage_categories.algebra.commutative_rings import (
    polynomial_ring as polynomial_ring,
)
from sage_categories.algebra.commutative_rings import (
    presented_ring_homomorphism as presented_ring_homomorphism,
)
from sage_categories.cat.canonical import FinitePresentedCategory as FinitePresentedCategory
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
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
from sage_categories.cat.structured_objects import Rings as Rings
from sage_categories.engines import oscar as oscar
from sage_categories.engines.julia_bridge import OscarHandle as OscarHandle
from sage_categories.geometry.affine import (
    AffineOpenCategory as AffineOpenCategory,
)
from sage_categories.geometry.affine import (
    AffineSchemesCategory as AffineSchemesCategory,
)
from sage_categories.geometry.affine import (
    Spec as Spec,
)
from sage_categories.geometry.affine import (
    affine_structure_sheaf as affine_structure_sheaf,
)
from sage_categories.geometry.affine import (
    native_affine_scheme as native_affine_scheme,
)
from sage_categories.geometry.sheaves import RingPresheaf as RingPresheaf
from sage_categories.geometry.sheaves import ring_presheaf_from_functor as ring_presheaf_from_functor

__all__ = ["ProjectiveLinePresentation", "Schemes", "SchemesCategory", "TwoChartGluing", "native_scheme", "native_scheme_morphism", "projective_line"]

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

class _StaticRoles_SchemesCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, construction: object) -> None: ...
        def construction(self) -> object: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        ...

        def domain(self) -> SchemesCategory.ObjectType: ...
        def codomain(self) -> SchemesCategory.ObjectType: ...

class SchemesCategory(
    _StaticRoles_SchemesCategory,
    Category[Any, Any, _StaticRoles_SchemesCategory.ObjectType, _StaticRoles_SchemesCategory.ElementType, _StaticRoles_SchemesCategory.MorphismType],
):
    def __init__(self) -> None: ...
    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType: ...
    def glue_two_affines(
        self,
        left: AffineSchemesCategory.ObjectType,
        right: AffineSchemesCategory.ObjectType,
        left_open: AffineOpenCategory.ObjectType,
        right_open: AffineOpenCategory.ObjectType,
        left_to_right_pullback: MorphismCategory.ObjectType,
        right_to_left_pullback: MorphismCategory.ObjectType,
    ) -> tuple[SchemesCategory.ObjectType, SchemesCategory.MorphismType, SchemesCategory.MorphismType]: ...
    def gluing_mediator(
        self, glued: SchemesCategory.ObjectType, target: SchemesCategory.ObjectType, left_map: SchemesCategory.MorphismType, right_map: SchemesCategory.MorphismType
    ) -> SchemesCategory.MorphismType: ...
    def chart_map(
        self,
        source: AffineSchemesCategory.ObjectType,
        target: SchemesCategory.ObjectType,
        target_chart: AffineSchemesCategory.ObjectType,
        pullback: MorphismCategory.ObjectType,
    ) -> SchemesCategory.MorphismType: ...

@cache
def Schemes() -> SchemesCategory: ...
def native_scheme(value: CategoryOfCategories.ElementType) -> NativeObjectRealization[OscarHandle, object]: ...
def native_scheme_morphism(value: MorphismCategory.ObjectType) -> NativeMorphismRealization[OscarHandle]: ...
def projective_line(field: CategoryOfCategories.ElementType) -> ProjectiveLinePresentation: ...
