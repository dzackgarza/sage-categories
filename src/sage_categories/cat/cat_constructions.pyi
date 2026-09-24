from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import partial

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.category import member as member
from sage_categories.cat.cones import cone as cone
from sage_categories.cat.cones import cone_apex as cone_apex
from sage_categories.cat.cones import vertex_of as vertex_of
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.diagrams import cospan_diagram as cospan_diagram
from sage_categories.cat.diagrams import sequence_position as sequence_position
from sage_categories.cat.functors import Cat as Cat
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.opposites import opposite_morphism as opposite_morphism
from sage_categories.cat.predicates import Predicate as Predicate
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.predicates import Unknown as Unknown
from sage_categories.cat.predicates import UnknownClass as UnknownClass
from sage_categories.cat.predicates import ask as ask
from sage_categories.cat.predicates import conjunction as conjunction
from sage_categories.cat.predicates import decide as decide
from sage_categories.cat.predicates import register_handler as register_handler
from sage_categories.cat.predicates import unconditional as unconditional
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.shapes import DiscreteCategory as DiscreteCategory
from sage_categories.cat.shapes import DiscreteObjectCategory as DiscreteObjectCategory
from sage_categories.cat.shapes import carrier_comparison as carrier_comparison
from sage_categories.kernel.construction import retained_input as retained_input
from sage_categories.kernel.refinement import is_placed as is_placed
from sage_categories.kernel.retention import (
    complete_constructions as complete_constructions,
)
from sage_categories.kernel.retention import deferred_category as deferred_category
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["LimitCategory", "LimitSubcategory", "limit_of_categories", "product_of_categories", "pullback_of_categories"]
type ObjectRule = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]
type MorphismRule = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class FamilyObjectData:
    diagram: Functor
    rule: ObjectRule

    def component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType: ...

@dataclass(frozen=True, eq=False, slots=True)
class FamilyMorphismData:
    diagram: Functor
    rule: MorphismRule

    def component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType: ...

class _StaticRoles_LimitCategory:
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def __init__(self, data: FamilyObjectData) -> None: ...
        def family_component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType: ...

    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def __init__(self, data: FamilyMorphismData) -> None: ...
        def family_component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType: ...
        def domain(self) -> LimitCategory.ObjectType: ...
        def codomain(self) -> LimitCategory.ObjectType: ...

class LimitCategory[
    ObjectRole = _StaticRoles_LimitCategory.ObjectType,
    ElementRole = _StaticRoles_LimitCategory.ElementType,
    MorphismRole = _StaticRoles_LimitCategory.MorphismType,
](_StaticRoles_LimitCategory, Category[[MorphismRule | tuple[MorphismCategory.ObjectType, ...]], [], ObjectRole, ElementRole, MorphismRole]):
    def __init__(self, diagram: Functor) -> None: ...
    def shape(self) -> Category: ...
    def defining_diagram(self) -> Functor: ...
    def factor(self, index: CategoryOfCategories.ElementType | Hashable) -> Category: ...
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition: ...
    @cached_method
    def object_set(self) -> CategoryOfCategories.ElementType: ...
    def object_at(self, point: CategoryOfCategories.ElementType) -> ObjectRole: ...
    def morphism_at(self, point: CategoryOfCategories.ElementType) -> MorphismRole: ...
    def __call__(
        self, family: ObjectRule | CategoryOfCategories.ElementType | tuple[CategoryOfCategories.ElementType, ...], *components: CategoryOfCategories.ElementType
    ) -> ObjectRole: ...
    def from_components(self, rule: ObjectRule) -> ObjectRole: ...
    def construct_morphism(self, domain: ObjectRole, codomain: ObjectRole, family: MorphismRule | tuple[MorphismCategory.ObjectType, ...]) -> MorphismRole: ...
    def morphism_from_components(self, domain: ObjectRole, codomain: ObjectRole, rule: MorphismRule) -> MorphismRole: ...
    def construct_identity(self, member_object: ObjectRole) -> MorphismRole: ...
    def composite(self, second: MorphismRole, first: MorphismRole) -> MorphismRole: ...

class _StaticRoles_LimitSubcategory(_StaticRoles_LimitCategory):
    class ObjectType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory): ...
    class ElementType(sage_categories.cat.category._StaticRoles_CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms._StaticRoles_MorphismCategory.ObjectType):
        def domain(self) -> LimitSubcategory.ObjectType: ...
        def codomain(self) -> LimitSubcategory.ObjectType: ...

class LimitSubcategory[
    ObjectRole = _StaticRoles_LimitSubcategory.ObjectType,
    ElementRole = _StaticRoles_LimitSubcategory.ElementType,
    MorphismRole = _StaticRoles_LimitSubcategory.MorphismType,
](_StaticRoles_LimitSubcategory, LimitCategory[ObjectRole, ElementRole, MorphismRole]):
    def __init__(self, diagram: Functor) -> None: ...
    def family_category(self, diagram: Functor) -> LimitCategory: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...

def limit_of_categories(diagram: Functor, family: Category, category_type: type[LimitCategory] | partial[LimitCategory] = ...) -> CategoryOfCategories.ElementType: ...
def product_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType: ...
def pullback_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType: ...
def _faithful_isofibration_projection(limit: LimitCategory, index: int) -> Functor: ...
def _limit_of_opposite_categories(diagram: Functor) -> CategoryOfCategories.ElementType: ...
