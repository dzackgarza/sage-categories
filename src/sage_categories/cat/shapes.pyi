from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
__all__ = ['DiscreteCategory', 'Discrete', 'is_discrete', 'index_set_of', 'ThinCategory', 'Thin', 'omega']

@dataclass(frozen=True, eq=False, slots=True)
class DiscreteObjectData:
    point: CategoryOfCategories.ElementType

class DiscreteCategory(Category[[], []]):

    class ObjectType:

        def __init__(self, data: DiscreteObjectData) -> None:
            ...

        def point(self) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType:
        ...

    class ElementType:
        ...

    def __init__(self, index_set: CategoryOfCategories.ElementType) -> None:
        ...

    def index_set(self) -> CategoryOfCategories.ElementType:
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
Discrete: Functor

def is_discrete(shape: Category) -> bool:
    ...

def index_set_of(shape: Category) -> CategoryOfCategories.ElementType:
    ...

@dataclass(frozen=True, eq=False, slots=True)
class ThinObjectData:
    point: CategoryOfCategories.ElementType

class ThinMorphisms(MorphismCategory[[], []]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

class ThinCategory(Category[[], []]):

    class ObjectType:

        def __init__(self, data: ThinObjectData) -> None:
            ...

        def point(self) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType:
        ...

    class ElementType:
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
