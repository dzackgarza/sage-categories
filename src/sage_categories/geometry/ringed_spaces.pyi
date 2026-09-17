from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun, Functor as Functor, NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.spaces import TopologicalSpacesCategory as TopologicalSpacesCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function, cached_method as cached_method
from typing import Generic
from typing_extensions import TypeVar
OpenKey = TypeVar('OpenKey', bound=Hashable, default=Hashable)
type SheafComponentRule[OpenKey: Hashable] = Callable[[OpenKey], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData[OpenKey: Hashable]:
    space: TopologicalSpacesCategory.ObjectType[OpenKey]
    sheaf: RingSheaf[OpenKey]

class RingedSpacesCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType(Generic[OpenKey]):

        def __init__(self, data: _RingedSpaceData[OpenKey]) -> None:
            ...

        def space(self) -> TopologicalSpacesCategory.ObjectType[OpenKey]:
            ...

        def sheaf(self) -> RingSheaf[OpenKey]:
            ...

    class ElementType:
        ...

    class MorphismType:

        def __init__(self, data: tuple[MorphismCategory.ObjectType, NaturalTransformation]) -> None:
            ...

        def continuous_map(self) -> MorphismCategory.ObjectType:
            ...

        def sheaf_map(self) -> NaturalTransformation:
            ...

    @cached_method
    def to_spaces(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def __call__[OpenKey: Hashable](self, space: TopologicalSpacesCategory.ObjectType[OpenKey], sheaf: RingSheaf[OpenKey]) -> RingedSpacesCategory.ObjectType[OpenKey]:
        ...

    def homomorphism[SourceKey: Hashable, TargetKey: Hashable](self, source: RingedSpacesCategory.ObjectType[SourceKey], target: RingedSpacesCategory.ObjectType[TargetKey], continuous: MorphismCategory.ObjectType, component_rule: SheafComponentRule[TargetKey]) -> RingedSpacesCategory.MorphismType:
        ...

def RingedSpaces() -> RingedSpacesCategory:
    ...
