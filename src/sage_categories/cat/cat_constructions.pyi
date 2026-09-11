import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from functools import partial
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
__all__ = ['LimitCategory', 'LimitSubcategory', 'limit_of_categories', 'product_of_categories', 'pullback_of_categories']
type ObjectRule = Callable[['CategoryOfCategories.ElementType'], 'CategoryOfCategories.ElementType']
type MorphismRule = Callable[['CategoryOfCategories.ElementType'], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class FamilyObjectData:
    diagram: Functor
    rule: ObjectRule

    def component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
        ...

@dataclass(frozen=True, eq=False, slots=True)
class FamilyMorphismData:
    diagram: Functor
    rule: MorphismRule

    def component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
        ...

class _ComponentsAgreePredicate(Predicate):
    name: str

class _StaticRoles_LimitCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def family_component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: FamilyMorphismData) -> None:
            ...

        def family_component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> LimitCategory.ObjectType:
            ...

        def codomain(self) -> LimitCategory.ObjectType:
            ...

class LimitCategory[_ObjectRole = _StaticRoles_LimitCategory.ObjectType, _ElementRole = _StaticRoles_LimitCategory.ElementType, _MorphismRole = _StaticRoles_LimitCategory.MorphismType](_StaticRoles_LimitCategory, Category[[MorphismRule | tuple[MorphismCategory.ObjectType, ...]], [], _ObjectRole, _ElementRole, _MorphismRole]):

    def __init__(self, diagram: Functor) -> None:
        ...

    def shape(self) -> Category:
        ...

    def defining_diagram(self) -> Functor:
        ...

    def factor(self, index: CategoryOfCategories.ElementType | Hashable) -> Category:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> _ObjectRole:
        ...

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> _MorphismRole:
        ...

    def __call__(self, family: ObjectRule | CategoryOfCategories.ElementType | tuple[CategoryOfCategories.ElementType, ...], *components: CategoryOfCategories.ElementType) -> _ObjectRole:
        ...

    def from_components(self, rule: ObjectRule) -> _ObjectRole:
        ...

    def construct_morphism(self, domain: _ObjectRole, codomain: _ObjectRole, family: MorphismRule | tuple[MorphismCategory.ObjectType, ...]) -> _MorphismRole:
        ...

    def morphism_from_components(self, domain: _ObjectRole, codomain: _ObjectRole, rule: MorphismRule) -> _MorphismRole:
        ...

    def construct_identity(self, member_object: _ObjectRole) -> _MorphismRole:
        ...

    def composite(self, second: _MorphismRole, first: _MorphismRole) -> _MorphismRole:
        ...

class _StaticRoles_LimitSubcategory(_StaticRoles_LimitCategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> LimitSubcategory.ObjectType:
            ...

        def codomain(self) -> LimitSubcategory.ObjectType:
            ...

class LimitSubcategory(_StaticRoles_LimitSubcategory, LimitCategory[_StaticRoles_LimitSubcategory.ObjectType, _StaticRoles_LimitSubcategory.ElementType, _StaticRoles_LimitSubcategory.MorphismType]):

    def __init__(self, diagram: Functor) -> None:
        ...

    def family_category(self, diagram: Functor) -> LimitCategory:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

def limit_of_categories(diagram: Functor, family: Category, category_type: type[LimitCategory] | partial[LimitCategory]=...) -> CategoryOfCategories.ElementType:
    ...

def product_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...

def pullback_of_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class _TaggedObjectData:
    tag: CategoryOfCategories.ElementType
    member: CategoryOfCategories.ElementType

@dataclass(frozen=True, eq=False, slots=True)
class _TaggedMorphismData:
    morphism: MorphismCategory.ObjectType

class _StaticRoles__TaggedCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: _TaggedObjectData) -> None:
            ...

        def tag(self) -> CategoryOfCategories.ElementType:
            ...

        def member(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: _TaggedMorphismData) -> None:
            ...

        def morphism(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> _TaggedCategory.ObjectType:
            ...

        def codomain(self) -> _TaggedCategory.ObjectType:
            ...

class _TaggedCategory(_StaticRoles__TaggedCategory, Category[[MorphismCategory.ObjectType], [], _StaticRoles__TaggedCategory.ObjectType, _StaticRoles__TaggedCategory.ElementType, _StaticRoles__TaggedCategory.MorphismType]):

    def __init__(self, diagram: Functor) -> None:
        ...

    def shape(self) -> Category:
        ...

    def summand(self, index: CategoryOfCategories.ElementType | Hashable) -> Category:
        ...

    def __call__(self, index: CategoryOfCategories.ElementType | Hashable, member_object: CategoryOfCategories.ElementType) -> _TaggedCategory.ObjectType:
        ...

    def construct_morphism(self, domain: _TaggedCategory.ObjectType, codomain: _TaggedCategory.ObjectType, morphism: MorphismCategory.ObjectType) -> _TaggedCategory.MorphismType:
        ...

    def construct_identity(self, member_object: _TaggedCategory.ObjectType) -> _TaggedCategory.MorphismType:
        ...

    def composite(self, second: _TaggedCategory.MorphismType, first: _TaggedCategory.MorphismType) -> _TaggedCategory.MorphismType:
        ...

def _limit_of_opposite_categories(diagram: Functor) -> CategoryOfCategories.ElementType:
    ...
