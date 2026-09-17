from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function, cached_method as cached_method
from sage_categories.order.posets import BinaryRelations as BinaryRelations, Posets as Posets, Thin as Thin
from typing import Generic
from typing_extensions import TypeVar
OpenKey = TypeVar('OpenKey', bound=Hashable, default=Hashable)

@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData[OpenKey: Hashable]:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType
    open_category: Category
    open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]
    open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]

class TopologicalSpacesCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType(Generic[OpenKey]):

        def __init__(self, data: _TopologyData[OpenKey]) -> None:
            ...

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def opens(self) -> CategoryOfCategories.ElementType:
            ...

        def open_category(self) -> Category:
            ...

        def open_point(self, key: OpenKey) -> CategoryOfCategories.ElementType:
            ...

        def open_object(self, key: OpenKey) -> CategoryOfCategories.ElementType:
            ...

    class ElementType:
        ...

    class MorphismType:

        def __init__(self, data: tuple[MorphismCategory.ObjectType, Functor]) -> None:
            ...

        def underlying_map(self) -> MorphismCategory.ObjectType:
            ...

        def inverse_image(self) -> Functor:
            ...

    @cached_method
    def to_sets(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType, opens: tuple[frozenset[Hashable], ...]) -> TopologicalSpacesCategory.ObjectType[frozenset[Hashable]]:
        ...

    def from_open_category[OpenKey: Hashable](self, carrier: CategoryOfCategories.ElementType, opens: CategoryOfCategories.ElementType, open_category: Category, open_point_rule: Callable[[OpenKey], CategoryOfCategories.ElementType], open_object_rule: Callable[[OpenKey], CategoryOfCategories.ElementType]) -> TopologicalSpacesCategory.ObjectType[OpenKey]:
        ...

    def construct_morphism(self, source: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]], target: TopologicalSpacesCategory.ObjectType[frozenset[Hashable]], underlying: MorphismCategory.ObjectType) -> TopologicalSpacesCategory.MorphismType:
        ...

    def morphism_with_inverse_image[SourceKey: Hashable, TargetKey: Hashable](self, source: TopologicalSpacesCategory.ObjectType[SourceKey], target: TopologicalSpacesCategory.ObjectType[TargetKey], underlying: MorphismCategory.ObjectType, inverse: Functor) -> TopologicalSpacesCategory.MorphismType:
        ...

    def construct_identity[OpenKey: Hashable](self, member_object: TopologicalSpacesCategory.ObjectType[OpenKey]) -> TopologicalSpacesCategory.MorphismType:
        ...

    def composite(self, second: TopologicalSpacesCategory.MorphismType, first: TopologicalSpacesCategory.MorphismType) -> TopologicalSpacesCategory.MorphismType:
        ...

def TopologicalSpaces() -> TopologicalSpacesCategory:
    ...

def _topological_space_projection(source: Category) -> Functor:
    ...
