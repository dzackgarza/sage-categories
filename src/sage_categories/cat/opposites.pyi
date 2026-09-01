from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition
from typing import Any
__all__ = ['OppositeCategory', 'opposite_category', 'opposite_morphism', 'Op', 'opposite_functor', 'opposite_transformation', 'op_squared_isomorphism']

@dataclass(frozen=True, eq=False, slots=True)
class _OppositeMorphismData:
    original: MorphismCategory.ObjectType

class OppositeCategory[**MorphismData, **TwoMorphismData](Category[[MorphismCategory.ObjectType], []]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:

        def __init__(self, data: _OppositeMorphismData) -> None:
            ...

        def original(self) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, original: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def original(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def is_discrete(self) -> bool:
        ...

    def narrowing_base(self) -> Category:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, original: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def limit_construction(self, shape: Category) -> Any:
        ...

    def colimit_construction(self, shape: Category) -> Any:
        ...

def opposite_category(category: Category) -> Category:
    ...

def opposite_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...
Op: Functor

def opposite_functor(functor: Functor) -> Functor:
    ...

def opposite_transformation(transformation: NaturalTransformation) -> NaturalTransformation:
    ...

def op_squared_isomorphism() -> NaturalTransformation:
    ...
