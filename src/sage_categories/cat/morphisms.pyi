import sage_categories
from _typeshed import Incomplete
from sage_categories.cat.category import Category, CategoryOfCategories, Decision, Predicate, Proposition
from sage_categories.cat.functors import Functor
from sage_categories.cat.properties import FixedEndpointProperty, FullSubcategory, PredicateSubcategory, PropertySubcategory
from typing import Literal, overload
__all__ = ['Mor', 'hom_inhabitation', 'MorphismCategory', 'IsomorphismsCategory', 'EndomorphismsCategory', 'FixedEndpointCategory']

@overload
def Mor[**M, **T](category: Category[M, T]) -> MorphismCategory[M, T]:
    ...

@overload
def Mor[**M, **T](level: Literal[0], category: Category[M, T]) -> Category[M, T]:
    ...

@overload
def Mor[**M, **T](level: Literal[1], category: Category[M, T]) -> MorphismCategory[M, T]:
    ...

@overload
def Mor[**M, **T](level: Literal[2], category: Category[M, T]) -> MorphismCategory[T, []]:
    ...

@overload
def Mor(level: int, category: Category) -> MorphismCategory[[], []]:
    ...

def hom_inhabitation(hom_category: Category) -> Decision:
    ...

class MorphismCategory[**MorphismData, **TwoMorphismData](Category[TwoMorphismData, []]):

    class ObjectType:

        def domain(self) -> CategoryOfCategories.ElementType:
            ...

        def codomain(self) -> CategoryOfCategories.ElementType:
            ...

        def base_category(self) -> Category:
            ...

        def retain_factors(self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> None:
            ...

        def is_composite(self) -> bool:
            ...

        def word(self) -> tuple[MorphismCategory.ObjectType, ...]:
            ...

        def factors(self) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
            ...

        def op(self) -> MorphismCategory.ObjectType:
            ...

        def __mul__(self, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

        def __eq__(self, candidate: MorphismCategory.ObjectType | int) -> Predicate:
            ...

        def __ne__(self, candidate: MorphismCategory.ObjectType | int) -> Proposition:
            ...

        def __hash__(self) -> int:
            ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.kernel.roles.ElementOfObject):
        ...

    def __init__(self, base: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def base_category(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def subcategory_monomorphism(self) -> Functor:
        ...

    def has_ambient(self) -> bool:
        ...

    def has_full_ambient(self) -> bool:
        ...

    def ambient(self) -> Category:
        ...

    def narrowing_base(self) -> Category:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def equality(self) -> Predicate:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType) -> FixedEndpointCategory[MorphismData, TwoMorphismData]:
        ...

    def fixed_endpoint_type(self) -> type[FixedEndpointCategory[MorphismData, TwoMorphismData]]:
        ...

    def construct_identity(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_morphism(self, source: MorphismCategory.ObjectType, target: MorphismCategory.ObjectType, *args: TwoMorphismData.args, **kwargs: TwoMorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...
    Monomorphisms: Incomplete
    Epimorphisms: Incomplete
    Isomorphisms: Incomplete
    Endomorphisms: Incomplete
    Identity: Incomplete

    def Automorphisms(self) -> Category:
        ...

class IsomorphismsCategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData]):

    class ElementType(sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.cat.morphisms.MorphismCategory.ElementType, sage_categories.kernel.roles.ElementOfObject, sage_categories.cat.functors.FunctorsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.cat.morphisms.MorphismCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType, sage_categories.cat.functors.FunctorsCategory.MorphismType):
        ...

    class ObjectType(sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType, sage_categories.cat.category.CategoryOfCategories.MorphismType):

        def inverse(self) -> MorphismCategory.ObjectType:
            ...

class EndomorphismsCategory[**MorphismData, **TwoMorphismData](PredicateSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

class FixedEndpointCategory[**MorphismData, **TwoMorphismData](FullSubcategory[TwoMorphismData, []]):

    class ObjectType(sage_categories.cat.functors.FunctorCategory.MorphismType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.morphisms.MorphismCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, morphisms: MorphismCategory[MorphismData, TwoMorphismData], domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType) -> None:
        ...

    def domain(self) -> CategoryOfCategories.ElementType:
        ...

    def codomain(self) -> CategoryOfCategories.ElementType:
        ...

    def narrowing_base(self) -> Category:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...

    def one(self) -> MorphismCategory.ObjectType:
        ...

    def compose(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def Monomorphisms(self) -> Category:
        ...

    def Epimorphisms(self) -> Category:
        ...

    def Isomorphisms(self) -> Category:
        ...

    def Endomorphisms(self) -> Category:
        ...

    def Identity(self) -> Category:
        ...

    def narrowing_type(self) -> type[FixedEndpointProperty[MorphismData, TwoMorphismData]]:
        ...
