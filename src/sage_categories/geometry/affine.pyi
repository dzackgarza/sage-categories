from dataclasses import dataclass

from _typeshed import Incomplete

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.opposites
import sage_categories.cat.structured_objects
import sage_categories.kernel.roles
from sage_categories.algebra.commutative_rings import PrimeIdeal as PrimeIdeal
from sage_categories.algebra.commutative_rings import (
    induced_stalk_map_to as induced_stalk_map_to,
)
from sage_categories.algebra.commutative_rings import (
    localization_extension as localization_extension,
)
from sage_categories.algebra.commutative_rings import (
    localize_at_prime as localize_at_prime,
)
from sage_categories.algebra.commutative_rings import prime_ideal as prime_ideal
from sage_categories.cat.assembly import chosen_construction as chosen_construction
from sage_categories.cat.assembly import has_selected_value as has_selected_value
from sage_categories.cat.assembly import select_value as select_value
from sage_categories.cat.assembly import selected_value as selected_value
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.leaf_categories import (
    ContravariantFaithfulStructureCategory as ContravariantFaithfulStructureCategory,
)
from sage_categories.cat.leaf_categories import (
    ParameterizedThinCategory as ParameterizedThinCategory,
)
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
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
from sage_categories.geometry.sheaves import RingPresheaf as RingPresheaf
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.sheaves import (
    ring_presheaf_from_functor as ring_presheaf_from_functor,
)
from sage_categories.geometry.sheaves import ring_sheaf as ring_sheaf
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory as TopologicalSpacesCategory,
)

__all__ = [
    "AffineOpen",
    "AffineOpenCategory",
    "AffineSchemes",
    "AffineSchemesCategory",
    "AffineSpectrumPoint",
    "AffineToLocallyRingedSpaces",
    "Spec",
    "affine_continuous_map",
    "affine_locally_ringed_map",
    "affine_locally_ringed_space",
    "affine_open_preimage",
    "affine_ring_sheaf",
    "affine_ringed_map",
    "affine_ringed_space",
    "affine_structure_sheaf",
    "affine_topological_space",
    "native_affine_morphism",
    "native_affine_scheme",
]

@dataclass(frozen=True, eq=False, slots=True)
class AffineSpectrumPoint:
    scheme: AffineSchemesCategory.ObjectType
    prime: PrimeIdeal
    local_ring: CategoryOfCategories.ElementType
    localization: MorphismCategory.ObjectType

@dataclass(frozen=True, eq=False, slots=True)
class _AffineOpenData:
    scheme: AffineSchemesCategory.ObjectType
    section_ring: CategoryOfCategories.ElementType
    parent: AffineOpenCategory.ObjectType | None
    localizing_element: CategoryOfCategories.ElementType | None
    ancestors: tuple[AffineOpenCategory.ObjectType, ...]
    restrictions: tuple[tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType], ...]

class _StaticRoles_AffineOpenCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _AffineOpenData) -> None: ...
        def section_ring(self) -> CategoryOfCategories.ElementType: ...
        def scheme(self) -> AffineSchemesCategory.ObjectType: ...
        def parent_open(self) -> AffineOpenCategory.ObjectType | None: ...
        def localizing_element(self) -> CategoryOfCategories.ElementType | None: ...
        def restriction_to(self, ancestor: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType: ...
        def covering_pieces(self) -> tuple[AffineOpenCategory.ObjectType, ...]: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> AffineOpenCategory.ObjectType: ...
        def codomain(self) -> AffineOpenCategory.ObjectType: ...

class AffineOpenCategory(
    _StaticRoles_AffineOpenCategory,
    ParameterizedThinCategory[_StaticRoles_AffineOpenCategory.ObjectType, _StaticRoles_AffineOpenCategory.ElementType, _StaticRoles_AffineOpenCategory.MorphismType],
):
    def scheme(self) -> AffineSchemesCategory.ObjectType: ...
    def root(self) -> AffineOpenCategory.ObjectType: ...
    def restriction_map(self, smaller: AffineOpenCategory.ObjectType, larger: AffineOpenCategory.ObjectType) -> MorphismCategory.ObjectType: ...
    def principal_open(self, parent: AffineOpenCategory.ObjectType, element: CategoryOfCategories.ElementType) -> AffineOpenCategory.ObjectType: ...
    def finite_union(self, pieces: tuple[AffineOpenCategory.ObjectType, ...]) -> AffineOpenCategory.ObjectType: ...

AffineOpen: Incomplete

class _StaticRoles_AffineSchemesCategory:
    class ObjectType(sage_categories.cat.structured_objects._StaticRoles_RingCategory.ObjectType):
        def __init__(self, coordinate_ring: CategoryOfCategories.ElementType) -> None: ...
        def coordinate_ring(self) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.cat.opposites._StaticRoles_OppositeCategory.ElementType): ...

    class MorphismType(sage_categories.cat.opposites._StaticRoles_OppositeCategory.MorphismType):
        def __init__(self, pullback: MorphismCategory.ObjectType) -> None: ...
        def pullback(self) -> MorphismCategory.ObjectType: ...
        def domain(self) -> AffineSchemesCategory.ObjectType: ...
        def codomain(self) -> AffineSchemesCategory.ObjectType: ...

class AffineSchemesCategory(
    _StaticRoles_AffineSchemesCategory,
    ContravariantFaithfulStructureCategory[
        _StaticRoles_AffineSchemesCategory.ObjectType, _StaticRoles_AffineSchemesCategory.ElementType, _StaticRoles_AffineSchemesCategory.MorphismType
    ],
):
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def from_coordinate_ring(self, coordinate_ring: CategoryOfCategories.ElementType) -> AffineSchemesCategory.ObjectType: ...
    def construct_morphism(
        self, source: AffineSchemesCategory.ObjectType, target: AffineSchemesCategory.ObjectType, pullback: MorphismCategory.ObjectType
    ) -> AffineSchemesCategory.MorphismType: ...
    def spectrum_point(self, scheme: AffineSchemesCategory.ObjectType, generators: tuple[CategoryOfCategories.ElementType, ...]) -> AffineSpectrumPoint: ...
    def map_spectrum_point(self, mapping: AffineSchemesCategory.MorphismType, point: AffineSpectrumPoint) -> tuple[AffineSpectrumPoint, MorphismCategory.ObjectType]: ...

def AffineSchemes() -> AffineSchemesCategory: ...
def native_affine_scheme(value: CategoryOfCategories.ElementType): ...
def native_affine_morphism(value: MorphismCategory.ObjectType): ...

Spec: Functor

def affine_structure_sheaf(scheme: AffineSchemesCategory.ObjectType) -> tuple[AffineOpenCategory, RingPresheaf[AffineOpenCategory.ObjectType]]: ...
def affine_topological_space(scheme: AffineSchemesCategory.ObjectType) -> TopologicalSpacesCategory.ObjectType[AffineOpenCategory.ObjectType]: ...
def affine_open_preimage(
    mapping: AffineSchemesCategory.MorphismType, target_open: AffineOpenCategory.ObjectType
) -> tuple[AffineOpenCategory.ObjectType, MorphismCategory.ObjectType]: ...
def affine_continuous_map(mapping: AffineSchemesCategory.MorphismType) -> TopologicalSpacesCategory.MorphismType: ...
def affine_ring_sheaf(scheme: AffineSchemesCategory.ObjectType) -> RingSheaf[AffineOpenCategory.ObjectType]: ...
def affine_ringed_space(scheme: AffineSchemesCategory.ObjectType) -> RingedSpacesCategory.ObjectType[AffineOpenCategory.ObjectType]: ...
def affine_ringed_map(mapping: AffineSchemesCategory.MorphismType) -> RingedSpacesCategory.MorphismType: ...
def affine_locally_ringed_space(scheme: AffineSchemesCategory.ObjectType) -> LocallyRingedSpacesCategory.ObjectType[AffineOpenCategory.ObjectType]: ...
def affine_locally_ringed_map(mapping: AffineSchemesCategory.MorphismType) -> LocallyRingedSpacesCategory.MorphismType: ...

AffineToLocallyRingedSpaces: Functor
