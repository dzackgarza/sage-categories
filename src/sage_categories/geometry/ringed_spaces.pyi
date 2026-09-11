import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.sheaves import RingSheaf
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['RingedSpacesCategory', 'RingedSpaces']
type SheafComponentRule = Callable[[frozenset[Hashable]], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData:
    space: TopologicalSpacesCategory.ObjectType
    sheaf: RingSheaf

class RingedSpacesCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: _RingedSpaceData) -> None:
            ...

        def space(self) -> TopologicalSpacesCategory.ObjectType:
            ...

        def sheaf(self) -> RingSheaf:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: tuple[MorphismCategory.ObjectType, NaturalTransformation]) -> None:
            ...

        def continuous_map(self) -> MorphismCategory.ObjectType:
            ...

        def sheaf_map(self) -> NaturalTransformation:
            ...

        def domain(self) -> RingedSpacesCategory.ObjectType:
            ...

        def codomain(self) -> RingedSpacesCategory.ObjectType:
            ...

    @cached_method
    def to_spaces(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__(self, space: TopologicalSpacesCategory.ObjectType, sheaf: RingSheaf) -> RingedSpacesCategory.ObjectType:
        ...

    def homomorphism(self, source: RingedSpacesCategory.ObjectType, target: RingedSpacesCategory.ObjectType, continuous: MorphismCategory.ObjectType, component_rule: SheafComponentRule) -> RingedSpacesCategory.MorphismType:
        ...

def RingedSpaces() -> RingedSpacesCategory:
    ...
