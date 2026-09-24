from collections.abc import Hashable
from dataclasses import dataclass

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.geometry.locally_ringed_spaces
import sage_categories.kernel.roles
from sage_categories.algebra.commutative_rings import integer_ring as integer_ring
from sage_categories.algebra.commutative_rings import inverse_unit as inverse_unit
from sage_categories.algebra.commutative_rings import (
    localization_extension as localization_extension,
)
from sage_categories.algebra.commutative_rings import (
    polynomial_coefficient_map as polynomial_coefficient_map,
)
from sage_categories.algebra.commutative_rings import polynomial_ring as polynomial_ring
from sage_categories.algebra.commutative_rings import (
    presented_ring_homomorphism as presented_ring_homomorphism,
)
from sage_categories.algebra.commutative_rings import prime_contains as prime_contains
from sage_categories.algebra.commutative_rings import (
    prime_generators as prime_generators,
)
from sage_categories.algebra.commutative_rings import (
    prime_ideal_equal as prime_ideal_equal,
)
from sage_categories.algebra.commutative_rings import (
    prime_ideal_extension as prime_ideal_extension,
)
from sage_categories.algebra.commutative_rings import (
    prime_ideal_preimage as prime_ideal_preimage,
)
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.choices import ChosenConstruction as ChosenConstruction
from sage_categories.cat.choices import SelectedChoice as SelectedChoice
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Cat as Cat
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.leaf_categories import (
    ParameterizedThinCategory as ParameterizedThinCategory,
)
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import assume as assume
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.cat.slices import SliceLikeCategory as SliceLikeCategory
from sage_categories.geometry.affine import AffineOpenCategory as AffineOpenCategory
from sage_categories.geometry.affine import AffineSchemes as AffineSchemes
from sage_categories.geometry.affine import (
    AffineSchemesCategory as AffineSchemesCategory,
)
from sage_categories.geometry.affine import AffineSpectrumPoint as AffineSpectrumPoint
from sage_categories.geometry.affine import Spec as Spec
from sage_categories.geometry.affine import (
    affine_locally_ringed_map as affine_locally_ringed_map,
)
from sage_categories.geometry.affine import (
    affine_locally_ringed_space as affine_locally_ringed_space,
)
from sage_categories.geometry.affine import (
    affine_structure_sheaf as affine_structure_sheaf,
)
from sage_categories.geometry.affine import (
    affine_topological_space as affine_topological_space,
)
from sage_categories.geometry.locally_ringed_spaces import (
    LocallyRingedSpaces as LocallyRingedSpaces,
)
from sage_categories.geometry.locally_ringed_spaces import (
    LocallyRingedSpacesCategory as LocallyRingedSpacesCategory,
)
from sage_categories.geometry.ringed_spaces import RingedSpaces as RingedSpaces
from sage_categories.geometry.ringed_spaces import (
    RingedSpacesCategory as RingedSpacesCategory,
)
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.sheaves import (
    descent_chart_comparison as descent_chart_comparison,
)
from sage_categories.geometry.sheaves import descent_lift as descent_lift
from sage_categories.geometry.sheaves import descent_map as descent_map
from sage_categories.geometry.sheaves import descent_projection as descent_projection
from sage_categories.geometry.sheaves import descent_restriction as descent_restriction
from sage_categories.geometry.sheaves import (
    descent_section_ring as descent_section_ring,
)
from sage_categories.geometry.sheaves import (
    identity_sheaf_comparison as identity_sheaf_comparison,
)
from sage_categories.geometry.sheaves import (
    ring_presheaf_from_functor as ring_presheaf_from_functor,
)
from sage_categories.geometry.sheaves import ring_sheaf as ring_sheaf
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory as TopologicalSpacesCategory,
)

__all__ = [
    "AffineOpenChart",
    "AffineOverlap",
    "AffineOverlapPiece",
    "AffineToSchemes",
    "FiniteAffineGluing",
    "ProjectiveLinePresentation",
    "SchemeOpenCategory",
    "Schemes",
    "SchemesCategory",
    "native_scheme",
    "native_scheme_morphism",
    "projective_line",
]

@dataclass(frozen=True, eq=False, slots=True)
class AffineOpenChart:
    affine: AffineSchemesCategory.ObjectType
    open_immersion: SchemesCategory.MorphismType
    structure_sheaf_comparison: NaturalTransformation

@dataclass(frozen=True, eq=False, slots=True)
class AffineOverlapPiece:
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_to_right_pullback: MorphismCategory.ObjectType
    right_to_left_pullback: MorphismCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class AffineOverlap:
    left: int
    right: int
    pieces: tuple[AffineOverlapPiece, ...]
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class FiniteAffineGluing:
    charts: tuple[AffineSchemesCategory.ObjectType, ...]
    overlaps: tuple[AffineOverlap, ...]

    def overlap(self, first: int, second: int) -> AffineOverlap: ...

@dataclass(frozen=True, eq=False, slots=True)
class _SchemeOpenData:
    presentation: FiniteAffineGluing
    chart: int
    affine_open: AffineOpenCategory.ObjectType
    chart_opens: tuple[AffineOpenCategory.ObjectType, ...]

class _StaticRoles_SchemeOpenCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _SchemeOpenData) -> None: ...
        def presentation(self) -> FiniteAffineGluing: ...
        def chart(self) -> int: ...
        def affine_open(self) -> AffineOpenCategory.ObjectType: ...
        def chart_opens(self) -> tuple[AffineOpenCategory.ObjectType, ...]: ...
        def chart_open(self, index: int) -> AffineOpenCategory.ObjectType: ...
        def section_ring(self) -> CategoryOfCategories.ElementType: ...
        def restriction_to(self, larger: SchemeOpenCategory.ObjectType) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> SchemeOpenCategory.ObjectType: ...
        def codomain(self) -> SchemeOpenCategory.ObjectType: ...

class SchemeOpenCategory(
    _StaticRoles_SchemeOpenCategory,
    ParameterizedThinCategory[_StaticRoles_SchemeOpenCategory.ObjectType, _StaticRoles_SchemeOpenCategory.ElementType, _StaticRoles_SchemeOpenCategory.MorphismType],
):
    def presentation(self) -> FiniteAffineGluing: ...
    def open(self, chart: int, affine_open: AffineOpenCategory.ObjectType) -> SchemeOpenCategory.ObjectType: ...
    def from_chart_opens(self, chart_opens: tuple[AffineOpenCategory.ObjectType, ...]) -> SchemeOpenCategory.ObjectType: ...
    def restriction_map(self, smaller: SchemeOpenCategory.ObjectType, larger: SchemeOpenCategory.ObjectType) -> MorphismCategory.ObjectType: ...

@dataclass(frozen=True, eq=False, slots=True)
class ProjectiveLinePresentation:
    scheme: SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType]
    left_chart: AffineSchemesCategory.ObjectType
    right_chart: AffineSchemesCategory.ObjectType
    left_coordinate: CategoryOfCategories.ElementType
    right_coordinate: CategoryOfCategories.ElementType
    left_open: AffineOpenCategory.ObjectType
    right_open: AffineOpenCategory.ObjectType
    left_inclusion: SchemesCategory.MorphismType
    right_inclusion: SchemesCategory.MorphismType
    chart_swap: SchemesCategory.MorphismType
    structure_sheaf: RingSheaf[SchemeOpenCategory.ObjectType]
    overlap_swap: MorphismCategory.ObjectType
    left_scheme_open: SchemeOpenCategory.ObjectType
    right_scheme_open: SchemeOpenCategory.ObjectType
    overlap_scheme_open: SchemeOpenCategory.ObjectType
    base: SchemesCategory.ObjectType[AffineOpenCategory.ObjectType]
    structure_map: SchemesCategory.MorphismType
    over_base: SliceLikeCategory.ObjectType
    swap_over_base: SliceLikeCategory.MorphismType

class _StaticRoles_SchemesCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):
    class ObjectType[OpenKey: Hashable = Hashable](sage_categories.geometry.locally_ringed_spaces._StaticRoles_LocallyRingedSpacesCategory.ObjectType[OpenKey,]):
        def affine_cover(self) -> tuple[AffineOpenChart, ...]: ...
        def local_affineness(self) -> tuple[AffineOpenChart, ...]: ...
        def finite_affine_gluing(self) -> FiniteAffineGluing: ...
        def underlying_points(self) -> CategoryOfCategories.ElementType: ...
        def valued_points(self, ring: CategoryOfCategories.ElementType) -> MorphismCategory: ...
        def categorical_points(self) -> MorphismCategory: ...
        def over(self, base: SchemesCategory.ObjectType, structure_map: SchemesCategory.MorphismType) -> SliceLikeCategory.ObjectType: ...

    class ElementType(sage_categories.geometry.locally_ringed_spaces._StaticRoles_LocallyRingedSpacesCategory.ElementType): ...

    class MorphismType(sage_categories.geometry.locally_ringed_spaces._StaticRoles_LocallyRingedSpacesCategory.MorphismType):
        def domain(self) -> SchemesCategory.ObjectType: ...
        def codomain(self) -> SchemesCategory.ObjectType: ...

class SchemesCategory(
    _StaticRoles_SchemesCategory,
    PropertySubcategory[..., ..., _StaticRoles_SchemesCategory.ObjectType, _StaticRoles_SchemesCategory.ElementType, _StaticRoles_SchemesCategory.MorphismType],
):
    def valued_points(self, scheme: SchemesCategory.ObjectType, ring: CategoryOfCategories.ElementType) -> MorphismCategory: ...
    def categorical_points(self, scheme: SchemesCategory.ObjectType) -> MorphismCategory: ...
    def over_base(self, scheme: SchemesCategory.ObjectType, base: SchemesCategory.ObjectType, structure_map: SchemesCategory.MorphismType) -> SliceLikeCategory.ObjectType: ...
    def retain_affine_cover(self, scheme: SchemesCategory.ObjectType, charts: tuple[AffineOpenChart, ...]) -> None: ...
    def affine_overlap(self, charts: tuple[AffineSchemesCategory.ObjectType, ...], left: int, right: int, pieces: tuple[AffineOverlapPiece, ...]) -> AffineOverlap: ...
    def glue_affines(
        self, charts: tuple[AffineSchemesCategory.ObjectType, ...], overlaps: tuple[AffineOverlap, ...]
    ) -> SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType]: ...
    def gluing_mediator[SourceOpenKey: Hashable, TargetOpenKey: Hashable](
        self, source: SchemesCategory.ObjectType[SourceOpenKey], target: SchemesCategory.ObjectType[TargetOpenKey], chart_maps: tuple[SchemesCategory.MorphismType, ...]
    ) -> SchemesCategory.MorphismType: ...
    def affine(self, affine: AffineSchemesCategory.ObjectType) -> SchemesCategory.ObjectType[AffineOpenCategory.ObjectType]: ...
    def affine_morphism(self, mapping: AffineSchemesCategory.MorphismType) -> SchemesCategory.MorphismType: ...
    def to_locally_ringed_spaces(self) -> Functor: ...
    def to_ringed_spaces(self) -> Functor: ...
    def to_topological_spaces(self) -> Functor: ...

def Schemes() -> SchemesCategory: ...

AffineToSchemes: Functor

def native_scheme(value: CategoryOfCategories.ElementType): ...
def native_scheme_morphism(value: MorphismCategory.ObjectType): ...
def projective_line(field: CategoryOfCategories.ElementType) -> ProjectiveLinePresentation: ...
