from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.leaf_categories import MorphismDataCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from sage_categories.geometry.ringed_spaces import RingedSpacesCategory

__all__ = ["LocallyRingedSpaces", "LocallyRingedSpacesCategory"]

type LocalRingRule = Callable[
    [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition
]
type LocalMapRule = Callable[
    [CategoryOfCategories.ElementType, MorphismCategory.ObjectType], Proposition
]
type StalkRule = Callable[
    [CategoryOfCategories.ElementType], CategoryOfCategories.ElementType
]
type StalkMapRule = Callable[
    [CategoryOfCategories.ElementType], MorphismCategory.ObjectType
]

@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedSpaceData:
    ringed_space: RingedSpacesCategory.ObjectType
    stalk_rule: StalkRule
    local_ring_rule: LocalRingRule

@dataclass(frozen=True, eq=False, slots=True)
class _LocallyRingedMorphismData:
    ringed_map: RingedSpacesCategory.MorphismType
    stalk_map_rule: StalkMapRule
    local_map_rule: LocalMapRule

class LocallyRingedSpacesCategory(MorphismDataCategory):
    class ObjectType:
        def __init__(self, data: _LocallyRingedSpaceData) -> None: ...
        def ringed_space(self) -> RingedSpacesCategory.ObjectType: ...
        def space(self): ...
        def sheaf(self): ...
        def stalk(
            self, point: CategoryOfCategories.ElementType
        ) -> CategoryOfCategories.ElementType: ...
        def local_ring_condition(
            self, point: CategoryOfCategories.ElementType
        ) -> Proposition: ...

    class ElementType: ...

    class MorphismType:
        def __init__(self, data: _LocallyRingedMorphismData) -> None: ...
        def ringed_map(self) -> RingedSpacesCategory.MorphismType: ...
        def continuous_map(self) -> MorphismCategory.ObjectType: ...
        def sheaf_map(self): ...
        def stalk_map(
            self, source_point: CategoryOfCategories.ElementType
        ) -> MorphismCategory.ObjectType: ...
        def local_map_condition(
            self, source_point: CategoryOfCategories.ElementType
        ) -> Proposition: ...

    def to_ringed_spaces(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def __call__(
        self,
        ringed_space: RingedSpacesCategory.ObjectType,
        local_ring_rule: LocalRingRule,
    ) -> LocallyRingedSpacesCategory.ObjectType: ...
    def with_stalks(
        self,
        ringed_space: RingedSpacesCategory.ObjectType,
        stalk_rule: StalkRule,
        local_ring_rule: LocalRingRule,
    ) -> LocallyRingedSpacesCategory.ObjectType: ...
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
