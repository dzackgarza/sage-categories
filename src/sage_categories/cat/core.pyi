from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory
from sage_categories.cat.predicates import Proposition
__all__ = ['GroupoidsCategory', 'CoreCategory', 'CoreMorphismCategory', 'CoreFixedEndpointCategory', 'Core', 'U', 'epsilon']

class GroupoidsCategory(Category[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

class CoreCategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def isomorphisms(self) -> Category:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def morphism_category_type(self) -> type[CoreMorphismCategory]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...

    def compose_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def inverse_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def retain_inverses(self, forward: MorphismCategory.ObjectType, backward: MorphismCategory.ObjectType) -> None:
        ...

    def retained_inverse(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | None:
        ...

class CoreMorphismCategory(MorphismCategory):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def fixed_endpoint_type(self) -> type[CoreFixedEndpointCategory]:
        ...

class CoreFixedEndpointCategory(FixedEndpointCategory):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...
Core: Functor
U: Functor
epsilon: NaturalTransformation
