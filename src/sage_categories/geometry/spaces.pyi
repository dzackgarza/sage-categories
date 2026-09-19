from collections.abc import Callable, Hashable
from dataclasses import dataclass

import sage_categories.sets.finite
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.choices import SelectedChoice as SelectedChoice
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.leaf_categories import (
    MorphismDataCategory as MorphismDataCategory,
)
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.order.posets import BinaryRelations as BinaryRelations
from sage_categories.order.posets import Posets as Posets
from sage_categories.order.posets import Thin as Thin

__all__ = ["TopologicalSpaces", "TopologicalSpacesCategory"]

@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData[OpenKey: Hashable]:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType
    open_category: Category
    open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]

class _StaticRoles_TopologicalSpacesCategory:
    class ObjectType[OpenKey: Hashable = Hashable](sage_categories.sets.finite._StaticRoles_SetsCategory.ObjectType):
        def __init__(self, data: _TopologyData[OpenKey]) -> None: ...
        def carrier(self) -> CategoryOfCategories.ElementType: ...
        def opens(self) -> CategoryOfCategories.ElementType: ...
        def open_category(self) -> Category: ...
        def open_point(self, key: OpenKey) -> CategoryOfCategories.ElementType: ...
        def open_object(self, key: OpenKey) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.sets.finite._StaticRoles_SetsCategory.ElementType): ...

    class MorphismType(sage_categories.sets.finite._StaticRoles_SetsCategory.MorphismType):
        def __init__(self, data: tuple[MorphismCategory.ObjectType, Functor]) -> None: ...
        def underlying_map(self) -> MorphismCategory.ObjectType: ...
        def inverse_image(self) -> Functor: ...
        def domain(self) -> TopologicalSpacesCategory.ObjectType: ...
        def codomain(self) -> TopologicalSpacesCategory.ObjectType: ...

class TopologicalSpacesCategory(
    _StaticRoles_TopologicalSpacesCategory,
    MorphismDataCategory[
        _StaticRoles_TopologicalSpacesCategory.ObjectType, _StaticRoles_TopologicalSpacesCategory.ElementType, _StaticRoles_TopologicalSpacesCategory.MorphismType
    ],
):
    def to_sets(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self, carrier: CategoryOfCategories.ElementType, opens: tuple[frozenset[Hashable], ...]) -> TopologicalSpacesCategory.ObjectType[frozenset[Hashable]]: ...
    def from_open_category[OpenKey: Hashable](
        self,
        carrier: CategoryOfCategories.ElementType,
        opens: CategoryOfCategories.ElementType,
        open_category: Category,
        open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
        open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.ObjectType[OpenKey]: ...
    def quotient_from_open_category[OpenKey: Hashable](
        self,
        ambient: CategoryOfCategories.ElementType,
        equivalent: Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], object],
        opens: CategoryOfCategories.ElementType,
        open_category: Category,
        open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
        open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.ObjectType[OpenKey]: ...
    def quotient_projection(self, space: TopologicalSpacesCategory.ObjectType) -> MorphismCategory.ObjectType: ...
    def quotient_chart_morphism[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        tag_rule: Callable[[Hashable], Hashable],
        preimage_rule: Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.MorphismType: ...
    def quotient_mediator[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        chart_maps: tuple[TopologicalSpacesCategory.MorphismType, ...],
        representative_rule: Callable[[CategoryOfCategories.ElementType], tuple[int, CategoryOfCategories.ElementType]],
        assemble_open: Callable[[tuple[CategoryOfCategories.ElementType, ...]], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.MorphismType: ...
    def construct_morphism(
        self,
        source: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        target: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]],
        underlying: MorphismCategory.ObjectType,
    ) -> TopologicalSpacesCategory.MorphismType: ...
    def morphism_with_inverse_image[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: TopologicalSpacesCategory.ObjectType[SourceKey],
        target: TopologicalSpacesCategory.ObjectType[TargetKey],
        underlying: MorphismCategory.ObjectType,
        inverse: Functor,
    ) -> TopologicalSpacesCategory.MorphismType: ...

def TopologicalSpaces() -> TopologicalSpacesCategory: ...
def _topological_space_projection(source: Category) -> Functor: ...
