from collections.abc import Callable
from collections.abc import Hashable as Hashable
from dataclasses import dataclass

from _typeshed import Incomplete

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
from sage_categories.cat.predicates import Axiom as Axiom
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.geometry.ringed_spaces import RingedSpaces as RingedSpaces
from sage_categories.geometry.ringed_spaces import (
    RingedSpacesCategory as RingedSpacesCategory,
)
from sage_categories.geometry.sheaves import RingSheaf as RingSheaf
from sage_categories.geometry.spaces import (
    TopologicalSpacesCategory as TopologicalSpacesCategory,
)
from sage_categories.geometry.stalks import ring_stalk as ring_stalk
from sage_categories.geometry.stalks import ringed_stalk_map as ringed_stalk_map

__all__ = ["LocallyRingedSpaces", "LocallyRingedSpacesCategory"]
type LocalRingRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]
type LocalMapRule = Callable[[CategoryOfCategories.ElementType, MorphismCategory.ObjectType], Proposition]
type StalkRule = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]
type StalkMapRule = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedSpaceData[OpenKey: Hashable]:
    ringed_space: RingedSpacesCategory.ObjectType[OpenKey]
    stalk_rule: StalkRule
    local_ring_rule: LocalRingRule

@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedMorphismData:
    ringed_map: RingedSpacesCategory.MorphismType
    stalk_map_rule: StalkMapRule
    local_map_rule: LocalMapRule

class _StaticRoles_LocallyRingedSpacesCategory:
    class ObjectType[OpenKey: Hashable = Hashable](sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: _LocallyRingedSpaceData[OpenKey]) -> None: ...
        def ringed_space(self) -> RingedSpacesCategory.ObjectType[OpenKey]: ...
        def space(self) -> TopologicalSpacesCategory.ObjectType[OpenKey]: ...
        def sheaf(self) -> RingSheaf[OpenKey]: ...
        def stalk(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
        def local_ring_condition(self, point: CategoryOfCategories.ElementType) -> Proposition: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: _LocallyRingedMorphismData) -> None: ...
        def ringed_map(self) -> RingedSpacesCategory.MorphismType: ...
        def continuous_map(self) -> TopologicalSpacesCategory.MorphismType: ...
        def sheaf_map(self) -> NaturalTransformation: ...
        def stalk_map(self, source_point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...
        def local_map_condition(self, source_point: CategoryOfCategories.ElementType) -> Proposition: ...
        def domain(self) -> LocallyRingedSpacesCategory.ObjectType: ...
        def codomain(self) -> LocallyRingedSpacesCategory.ObjectType: ...

class LocallyRingedSpacesCategory(
    _StaticRoles_LocallyRingedSpacesCategory,
    MorphismDataCategory[
        _StaticRoles_LocallyRingedSpacesCategory.ObjectType, _StaticRoles_LocallyRingedSpacesCategory.ElementType, _StaticRoles_LocallyRingedSpacesCategory.MorphismType
    ],
):
    Scheme: Incomplete

    def to_ringed_spaces(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__[OpenKey: Hashable](
        self, ringed_space: RingedSpacesCategory.ObjectType[OpenKey], local_ring_rule: LocalRingRule
    ) -> LocallyRingedSpacesCategory.ObjectType[OpenKey]: ...
    def with_stalks[OpenKey: Hashable](
        self, ringed_space: RingedSpacesCategory.ObjectType[OpenKey], stalk_rule: StalkRule, local_ring_rule: LocalRingRule
    ) -> LocallyRingedSpacesCategory.ObjectType[OpenKey]: ...
    def homomorphism(
        self,
        source: LocallyRingedSpacesCategory.ObjectType,
        target: LocallyRingedSpacesCategory.ObjectType,
        ringed_map: RingedSpacesCategory.MorphismType,
        local_map_rule: LocalMapRule,
    ) -> LocallyRingedSpacesCategory.MorphismType: ...
    def homomorphism_with_stalks(
        self,
        source: LocallyRingedSpacesCategory.ObjectType,
        target: LocallyRingedSpacesCategory.ObjectType,
        ringed_map: RingedSpacesCategory.MorphismType,
        stalk_map_rule: StalkMapRule,
        local_map_rule: LocalMapRule,
    ) -> LocallyRingedSpacesCategory.MorphismType: ...

def LocallyRingedSpaces() -> LocallyRingedSpacesCategory: ...
