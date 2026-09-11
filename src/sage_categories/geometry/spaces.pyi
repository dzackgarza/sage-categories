from collections.abc import Callable
from collections.abc import Hashable as Hashable
from dataclasses import dataclass

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method
from sage_categories.order.posets import BinaryRelations as BinaryRelations
from sage_categories.order.posets import Posets as Posets
from sage_categories.order.posets import Thin as Thin

__all__ = ["TopologicalSpaces", "TopologicalSpacesCategory"]

@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType
    open_category: Category
    open_point_rule: Callable[[object], CategoryOfCategories.ElementType]
    open_object_rule: Callable[[object], CategoryOfCategories.ElementType]

class _StaticRoles_TopologicalSpacesCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _TopologyData) -> None: ...
        def carrier(self) -> CategoryOfCategories.ElementType: ...
        def opens(self) -> CategoryOfCategories.ElementType: ...
        def open_category(self) -> Category: ...
        def open_point(self, key: object) -> CategoryOfCategories.ElementType: ...
        def open_object(self, key: object) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: tuple[MorphismCategory.ObjectType, Functor]) -> None: ...
        def underlying_map(self) -> MorphismCategory.ObjectType: ...
        def inverse_image(self) -> Functor: ...
        def domain(self) -> TopologicalSpacesCategory.ObjectType: ...
        def codomain(self) -> TopologicalSpacesCategory.ObjectType: ...

class TopologicalSpacesCategory(
    _StaticRoles_TopologicalSpacesCategory,
    Category[
        [MorphismCategory.ObjectType],
        [],
        _StaticRoles_TopologicalSpacesCategory.ObjectType,
        _StaticRoles_TopologicalSpacesCategory.ElementType,
        _StaticRoles_TopologicalSpacesCategory.MorphismType,
    ],
):
    @cached_method
    def to_sets(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self, carrier: CategoryOfCategories.ElementType, opens: tuple[frozenset[Hashable], ...]) -> TopologicalSpacesCategory.ObjectType: ...
    def from_open_category(
        self,
        carrier: CategoryOfCategories.ElementType,
        opens: CategoryOfCategories.ElementType,
        open_category: Category,
        open_point_rule: Callable[[object], CategoryOfCategories.ElementType],
        open_object_rule: Callable[[object], CategoryOfCategories.ElementType],
    ) -> TopologicalSpacesCategory.ObjectType: ...
    def construct_morphism(
        self, source: TopologicalSpacesCategory.ObjectType, target: TopologicalSpacesCategory.ObjectType, underlying: MorphismCategory.ObjectType
    ) -> TopologicalSpacesCategory.MorphismType: ...
    def morphism_with_inverse_image(
        self, source: TopologicalSpacesCategory.ObjectType, target: TopologicalSpacesCategory.ObjectType, underlying: MorphismCategory.ObjectType, inverse: Functor
    ) -> TopologicalSpacesCategory.MorphismType: ...
    def construct_identity(self, member_object: TopologicalSpacesCategory.ObjectType) -> TopologicalSpacesCategory.MorphismType: ...
    def composite(self, second: TopologicalSpacesCategory.MorphismType, first: TopologicalSpacesCategory.MorphismType) -> TopologicalSpacesCategory.MorphismType: ...

def TopologicalSpaces() -> TopologicalSpacesCategory: ...
