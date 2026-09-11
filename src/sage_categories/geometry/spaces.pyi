import sage_categories.cat.category
import sage_categories.cat.morphisms
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['TopologicalSpacesCategory', 'TopologicalSpaces']

@dataclass(frozen=True, eq=False, slots=True)
class _TopologyData:
    carrier: CategoryOfCategories.ElementType
    opens: CategoryOfCategories.ElementType
    open_category: Category
    open_point_rule: Callable[[object], CategoryOfCategories.ElementType]
    open_object_rule: Callable[[object], CategoryOfCategories.ElementType]

class TopologicalSpacesCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def __init__(self, data: _TopologyData) -> None:
            ...

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def opens(self) -> CategoryOfCategories.ElementType:
            ...

        def open_category(self) -> Category:
            ...

        def open_point(self, key: object) -> CategoryOfCategories.ElementType:
            ...

        def open_object(self, key: object) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

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

    def __call__(self, carrier: CategoryOfCategories.ElementType, opens: tuple[frozenset[Hashable], ...]) -> TopologicalSpacesCategory.ObjectType:
        ...

    def from_open_category(self, carrier: CategoryOfCategories.ElementType, opens: CategoryOfCategories.ElementType, open_category: Category, open_point_rule: Callable[[object], CategoryOfCategories.ElementType], open_object_rule: Callable[[object], CategoryOfCategories.ElementType]) -> TopologicalSpacesCategory.ObjectType:
        ...

    def construct_morphism(self, source: TopologicalSpacesCategory.ObjectType, target: TopologicalSpacesCategory.ObjectType, underlying: MorphismCategory.ObjectType) -> TopologicalSpacesCategory.MorphismType:
        ...

    def morphism_with_inverse_image(self, source: TopologicalSpacesCategory.ObjectType, target: TopologicalSpacesCategory.ObjectType, underlying: MorphismCategory.ObjectType, inverse: Functor) -> TopologicalSpacesCategory.MorphismType:
        ...

    def construct_identity(self, member_object: TopologicalSpacesCategory.ObjectType) -> TopologicalSpacesCategory.MorphismType:
        ...

    def composite(self, second: TopologicalSpacesCategory.MorphismType, first: TopologicalSpacesCategory.MorphismType) -> TopologicalSpacesCategory.MorphismType:
        ...

def TopologicalSpaces() -> TopologicalSpacesCategory:
    ...
