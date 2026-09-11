from collections.abc import Callable, Hashable
from dataclasses import dataclass

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import ask as ask
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.spaces import TopologicalSpaces as TopologicalSpaces
from sage_categories.geometry.spaces import TopologicalSpacesCategory as TopologicalSpacesCategory
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["RingedSpaces", "RingedSpacesCategory"]
type SheafComponentRule = Callable[[frozenset[Hashable]], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class _RingedSpaceData:
    space: TopologicalSpacesCategory.ObjectType
    sheaf: RingSheaf

class _StaticRoles_RingedSpacesCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _RingedSpaceData) -> None: ...
        def space(self) -> TopologicalSpacesCategory.ObjectType: ...
        def sheaf(self) -> RingSheaf: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: tuple[MorphismCategory.ObjectType, NaturalTransformation]) -> None: ...
        def continuous_map(self) -> MorphismCategory.ObjectType: ...
        def sheaf_map(self) -> NaturalTransformation: ...
        def domain(self) -> RingedSpacesCategory.ObjectType: ...
        def codomain(self) -> RingedSpacesCategory.ObjectType: ...

class RingedSpacesCategory(
    _StaticRoles_RingedSpacesCategory,
    Category[
        [MorphismCategory.ObjectType],
        [],
        _StaticRoles_RingedSpacesCategory.ObjectType,
        _StaticRoles_RingedSpacesCategory.ElementType,
        _StaticRoles_RingedSpacesCategory.MorphismType,
    ],
):
    @cached_method
    def to_spaces(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(self, space: TopologicalSpacesCategory.ObjectType, sheaf: RingSheaf) -> RingedSpacesCategory.ObjectType: ...
    def homomorphism(
        self, source: RingedSpacesCategory.ObjectType, target: RingedSpacesCategory.ObjectType, continuous: MorphismCategory.ObjectType, component_rule: SheafComponentRule
    ) -> RingedSpacesCategory.MorphismType: ...

def RingedSpaces() -> RingedSpacesCategory: ...
