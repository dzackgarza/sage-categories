from collections.abc import Callable
from dataclasses import dataclass

import sage_categories.cat.structured_objects
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.leaf_categories import (
    MorphismDataCategory as MorphismDataCategory,
)
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import ask as ask
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory as TopologicalSpacesCategory,
)

__all__ = ["BinaryContinuity", "ProductTopologyOpen", "TopologicalRings", "TopologicalRingsCategory"]

@dataclass(frozen=True, eq=False, slots=True)
class ProductTopologyOpen:
    space: TopologicalSpacesCategory.ObjectType
    membership: Callable[[tuple[object, object]], bool | None]
    construction: object

    def contains(self, first: object, second: object) -> bool | None: ...

@dataclass(frozen=True, eq=False, slots=True)
class BinaryContinuity:
    space: TopologicalSpacesCategory.ObjectType
    operation: MorphismCategory.ObjectType
    preimage_rule: Callable[[CategoryOfCategories.ElementType], ProductTopologyOpen]

    def preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen: ...

@dataclass(frozen=True, eq=False, slots=True)
class _TopologicalRingData:
    ring: CategoryOfCategories.ElementType
    space: TopologicalSpacesCategory.ObjectType
    addition: BinaryContinuity
    multiplication: BinaryContinuity

class _StaticRoles_TopologicalRingsCategory:
    class ObjectType(sage_categories.cat.structured_objects._StaticRoles_RingCategory.ObjectType):
        def __init__(self, data: _TopologicalRingData) -> None: ...
        def ring(self) -> CategoryOfCategories.ElementType: ...
        def space(self) -> TopologicalSpacesCategory.ObjectType: ...
        def addition_continuity(self) -> BinaryContinuity: ...
        def multiplication_continuity(self) -> BinaryContinuity: ...
        def addition_preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen: ...
        def multiplication_preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen: ...

    class ElementType(sage_categories.cat.structured_objects._StaticRoles_RingCategory.ElementType): ...

    class MorphismType(sage_categories.cat.structured_objects._StaticRoles_RingCategory.MorphismType):
        def __init__(self, data: tuple[MorphismCategory.ObjectType, TopologicalSpacesCategory.MorphismType]) -> None: ...
        def ring_map(self) -> MorphismCategory.ObjectType: ...
        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType: ...
        def domain(self) -> TopologicalRingsCategory.ObjectType: ...
        def codomain(self) -> TopologicalRingsCategory.ObjectType: ...

class TopologicalRingsCategory(
    _StaticRoles_TopologicalRingsCategory,
    MorphismDataCategory[
        _StaticRoles_TopologicalRingsCategory.ObjectType, _StaticRoles_TopologicalRingsCategory.ElementType, _StaticRoles_TopologicalRingsCategory.MorphismType
    ],
):
    def to_rings(self) -> Functor: ...
    def to_spaces(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(
        self, ring: CategoryOfCategories.ElementType, space: TopologicalSpacesCategory.ObjectType, addition: BinaryContinuity, multiplication: BinaryContinuity
    ) -> TopologicalRingsCategory.ObjectType: ...
    def homomorphism(
        self,
        source: TopologicalRingsCategory.ObjectType,
        target: TopologicalRingsCategory.ObjectType,
        ring_map: MorphismCategory.ObjectType,
        continuous_map: TopologicalSpacesCategory.MorphismType,
    ) -> TopologicalRingsCategory.MorphismType: ...

def TopologicalRings() -> TopologicalRingsCategory: ...
