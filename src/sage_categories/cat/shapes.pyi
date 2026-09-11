import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
import sage_categories.sets.finite
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['DiscreteCategory', 'discrete_functor', 'Discrete', 'carrier_comparison', 'ThinCategory', 'Thin', 'omega']

@dataclass(frozen=True, eq=False, slots=True)
class DiscreteObjectData:
    point: CategoryOfCategories.ElementType

class DiscreteCategory(Category[[], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: DiscreteObjectData) -> None:
            ...

        def point(self) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    def __init__(self, index_set: CategoryOfCategories.ElementType) -> None:
        ...

    def index_set(self) -> CategoryOfCategories.ElementType:
        ...

    def is_discrete(self) -> bool:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.ObjectType:
        ...

    def object_point(self, member_object: DiscreteCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.MorphismType:
        ...

    def generating_morphisms(self) -> tuple[DiscreteCategory.MorphismType, ...]:
        ...

    def __call__(self, point: CategoryOfCategories.ElementType) -> DiscreteCategory.ObjectType:
        ...

    def construct_morphism(self, domain: DiscreteCategory.ObjectType, codomain: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        ...

    def construct_identity(self, member_object: DiscreteCategory.ObjectType) -> DiscreteCategory.MorphismType:
        ...

    def composite(self, second: DiscreteCategory.MorphismType, first: DiscreteCategory.MorphismType) -> DiscreteCategory.MorphismType:
        ...

def discrete_functor(sets: Category) -> Functor:
    ...
Discrete: Functor

class DiscreteObjectCategory(DiscreteCategory):

    class ObjectType(sage_categories.sets.finite.SetsCategory.ElementType, sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __call__(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_point(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    @cached_method
    def point_comparison(self) -> Functor:
        ...

def carrier_comparison(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> Proposition | None:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class ThinObjectData:
    point: CategoryOfCategories.ElementType

class _ComparablePredicate(Predicate):
    name: str

class ThinMorphisms(MorphismCategory[[], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

class ThinCategory(Category[[], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: ThinObjectData) -> None:
            ...

        def point(self) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    def __init__(self, carrier: CategoryOfCategories.ElementType, order: Predicate) -> None:
        ...

    def carrier(self) -> CategoryOfCategories.ElementType:
        ...

    def order(self) -> Predicate:
        ...

    def morphism_category_type(self) -> type[ThinMorphisms]:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> ThinCategory.ObjectType:
        ...

    def object_point(self, member_object: ThinCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def __call__(self, point: CategoryOfCategories.ElementType) -> ThinCategory.ObjectType:
        ...

    def construct_morphism(self, domain: ThinCategory.ObjectType, codomain: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        ...

    def construct_identity(self, member_object: ThinCategory.ObjectType) -> ThinCategory.MorphismType:
        ...

    def composite(self, second: ThinCategory.MorphismType, first: ThinCategory.MorphismType) -> ThinCategory.MorphismType:
        ...

def Thin(carrier: CategoryOfCategories.ElementType, order: Predicate) -> ThinCategory:
    ...

def omega() -> Category:
    ...

def realize_discrete_object(value: CategoryOfCategories.ElementType) -> None:
    ...
