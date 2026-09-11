import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['ProductTopologyOpen', 'BinaryContinuity', 'TopologicalRingsCategory', 'TopologicalRings']

@dataclass(frozen=True, eq=False, slots=True)
class ProductTopologyOpen:
    space: TopologicalSpacesCategory.ObjectType
    membership: Callable[[tuple[object, object]], bool | None]
    construction: object

    def contains(self, first: object, second: object) -> bool | None:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class BinaryContinuity:
    space: TopologicalSpacesCategory.ObjectType
    operation: MorphismCategory.ObjectType
    preimage_rule: Callable[[CategoryOfCategories.ElementType], ProductTopologyOpen]

    def preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class _TopologicalRingData:
    ring: CategoryOfCategories.ElementType
    space: TopologicalSpacesCategory.ObjectType
    addition: BinaryContinuity
    multiplication: BinaryContinuity

class TopologicalRingsCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: _TopologicalRingData) -> None:
            ...

        def ring(self) -> CategoryOfCategories.ElementType:
            ...

        def space(self) -> TopologicalSpacesCategory.ObjectType:
            ...

        def addition_continuity(self) -> BinaryContinuity:
            ...

        def multiplication_continuity(self) -> BinaryContinuity:
            ...

        def addition_preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen:
            ...

        def multiplication_preimage(self, open_object: CategoryOfCategories.ElementType) -> ProductTopologyOpen:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: tuple[MorphismCategory.ObjectType, TopologicalSpacesCategory.MorphismType]) -> None:
            ...

        def ring_map(self) -> MorphismCategory.ObjectType:
            ...

        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType:
            ...

        def domain(self) -> TopologicalRingsCategory.ObjectType:
            ...

        def codomain(self) -> TopologicalRingsCategory.ObjectType:
            ...

    @cached_method
    def to_rings(self) -> Functor:
        ...

    @cached_method
    def to_spaces(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self, ring: CategoryOfCategories.ElementType, space: TopologicalSpacesCategory.ObjectType, addition: BinaryContinuity, multiplication: BinaryContinuity) -> TopologicalRingsCategory.ObjectType:
        ...

    def homomorphism(self, source: TopologicalRingsCategory.ObjectType, target: TopologicalRingsCategory.ObjectType, ring_map: MorphismCategory.ObjectType, continuous_map: TopologicalSpacesCategory.MorphismType) -> TopologicalRingsCategory.MorphismType:
        ...

    def construct_identity(self, member_object: TopologicalRingsCategory.ObjectType) -> TopologicalRingsCategory.MorphismType:
        ...

    def composite(self, second: TopologicalRingsCategory.MorphismType, first: TopologicalRingsCategory.MorphismType) -> TopologicalRingsCategory.MorphismType:
        ...

def TopologicalRings() -> TopologicalRingsCategory:
    ...
