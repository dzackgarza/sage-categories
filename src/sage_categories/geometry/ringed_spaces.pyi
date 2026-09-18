from collections.abc import Callable
from collections.abc import Hashable as Hashable
from dataclasses import dataclass

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.leaf_categories import (
    MorphismDataCategory as MorphismDataCategory,
)
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory as TopologicalSpacesCategory,
)

__all__ = ["RingedSpaces", "RingedSpacesCategory"]
type SheafComponentRule[OpenKey: Hashable] = Callable[[OpenKey], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData[OpenKey: Hashable]:
    space: TopologicalSpacesCategory.ObjectType[OpenKey]
    sheaf: RingSheaf[OpenKey]

class _StaticRoles_RingedSpacesCategory:
    class ObjectType[OpenKey: Hashable = Hashable](sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _RingedSpaceData[OpenKey]) -> None: ...
        def space(self) -> TopologicalSpacesCategory.ObjectType[OpenKey]: ...
        def sheaf(self) -> RingSheaf[OpenKey]: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: tuple[TopologicalSpacesCategory.MorphismType, NaturalTransformation]) -> None: ...
        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType: ...
        def sheaf_map(self) -> NaturalTransformation: ...
        def domain(self) -> RingedSpacesCategory.ObjectType: ...
        def codomain(self) -> RingedSpacesCategory.ObjectType: ...

class RingedSpacesCategory(
    _StaticRoles_RingedSpacesCategory,
    MorphismDataCategory[_StaticRoles_RingedSpacesCategory.ObjectType, _StaticRoles_RingedSpacesCategory.ElementType, _StaticRoles_RingedSpacesCategory.MorphismType],
):
    def to_spaces(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__[OpenKey: Hashable](self, space: TopologicalSpacesCategory.ObjectType[OpenKey], sheaf: RingSheaf[OpenKey]) -> RingedSpacesCategory.ObjectType[OpenKey]: ...
    def homomorphism[SourceKey: Hashable, TargetKey: Hashable](
        self,
        source: RingedSpacesCategory.ObjectType[SourceKey],
        target: RingedSpacesCategory.ObjectType[TargetKey],
        continuous: TopologicalSpacesCategory.MorphismType,
        component_rule: SheafComponentRule[TargetKey],
    ) -> RingedSpacesCategory.MorphismType: ...

def RingedSpaces() -> RingedSpacesCategory: ...
