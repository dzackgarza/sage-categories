from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
__all__ = ['LimitCategory', 'limit_of_categories', 'product_of_categories', 'pullback_of_categories']
type ObjectRule = Callable[['CategoryOfCategories.ElementType'], 'CategoryOfCategories.ElementType']
type MorphismRule = Callable[['CategoryOfCategories.ElementType'], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class FamilyObjectData:
    rule: ObjectRule

@dataclass(frozen=True, eq=False, slots=True)
class FamilyMorphismData:
    rule: MorphismRule

class _ComponentsAgreePredicate(Predicate):
    name: str

class LimitCategory(Category[[MorphismRule | tuple[MorphismCategory.ObjectType, ...]], []]):

    class ObjectType:

        def __init__(self, data: FamilyObjectData) -> None:
            ...

        def component(self, index: CategoryOfCategories.ElementType | Hashable) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType:

        def __init__(self, data: FamilyMorphismData) -> None:
            ...

        def component(self, index: CategoryOfCategories.ElementType | Hashable) -> MorphismCategory.ObjectType:
            ...

    class ElementType:
        ...

    def __init__(self, diagram: Functor) -> None:
        ...

    def shape(self) -> Category:
        ...

    def factor(self, index: CategoryOfCategories.ElementType | Hashable) -> Category:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> LimitCategory.ObjectType:
        ...

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> LimitCategory.MorphismType:
        ...

    def __call__(self, family: ObjectRule | tuple[CategoryOfCategories.ElementType, ...]) -> LimitCategory.ObjectType:
        ...

    def construct_morphism(self, domain: LimitCategory.ObjectType, codomain: LimitCategory.ObjectType, family: MorphismRule | tuple[MorphismCategory.ObjectType, ...]) -> LimitCategory.MorphismType:
        ...

    def construct_identity(self, member_object: LimitCategory.ObjectType) -> LimitCategory.MorphismType:
        ...

    def composite(self, second: LimitCategory.MorphismType, first: LimitCategory.MorphismType) -> LimitCategory.MorphismType:
        ...

def limit_of_categories(diagram: Functor, family: Category, category_type: Callable[[Functor], LimitCategory]=...) -> CategoryOfCategories.ElementType:
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

class _TaggedCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType:

        def __init__(self, data: _TaggedObjectData) -> None:
            ...

        def tag(self) -> CategoryOfCategories.ElementType:
            ...

        def member(self) -> CategoryOfCategories.ElementType:
            ...

    class MorphismType:

        def __init__(self, data: _TaggedMorphismData) -> None:
            ...

        def morphism(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType:
        ...

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
