import sage_categories.cat.cat_constructions
import sage_categories.cat.category
import sage_categories.cat.constructions
import sage_categories.cat.functors
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.kernel.roles
import sage_categories.sets.finite
import abc
from collections.abc import Callable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition, UnknownClass
from typing import Literal
__all__ = ['FullSubcategory', 'InverseImageSubcategory', 'inverse_image', 'retain_inverse_image', 'PropertySubcategory', 'PredicateSubcategory', 'NarrowedProperty', 'FixedEndpointProperty']

class FullSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> FullSubcategory.ObjectType:
            ...

        def codomain(self) -> FullSubcategory.ObjectType:
            ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def has_ambient(self) -> bool:
        ...

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def narrowing_base(self) -> Category:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def element_from_defining_morphism(self, defining_morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def point_morphism(self, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def Terminal(self) -> CategoryOfCategories.ElementType:
        ...

    def image_factorization(self, arrow: MorphismCategory.ObjectType) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
        ...

    def factor_through_monomorphism(self, mono: MorphismCategory.ObjectType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | Literal[False] | UnknownClass:
        ...

    def hom_morphisms(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType) -> tuple[MorphismCategory.ObjectType, ...] | UnknownClass:
        ...

class InverseImageSubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.cat_constructions.LimitCategory.ObjectType, sage_categories.sets.finite.SetsCategory.ObjectType, sage_categories.cat.constructions.LimitsCategory.ElementType):
        ...

    class ElementType(sage_categories.cat.cat_constructions.LimitCategory.ElementType, sage_categories.sets.finite.SetsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.cat_constructions.LimitCategory.MorphismType, sage_categories.sets.finite.SetsCategory.MorphismType):
        ...

        def domain(self) -> InverseImageSubcategory.ObjectType:
            ...

        def codomain(self) -> InverseImageSubcategory.ObjectType:
            ...

    def __init__(self, functor: Functor, target_subcategory: Category) -> None:
        ...

    def defining_functor(self) -> Functor:
        ...

    def target_subcategory(self) -> Category:
        ...

    def subcategory_monomorphism(self) -> Functor:
        ...

    def target_projection(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__[Datum](self, *construction_data: Datum, **keywords: Datum) -> CategoryOfCategories.ElementType:
        ...

def inverse_image(functor: Functor, target_subcategory: Category) -> Category:
    ...

def retain_inverse_image(functor: Functor, target_subcategory: Category, realization: Category, source_projection: Functor, target_projection: Functor) -> None:
    ...

class PropertySubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> PropertySubcategory.ObjectType:
            ...

        def codomain(self) -> PropertySubcategory.ObjectType:
            ...

    def __init_subclass__(cls) -> None:
        ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], name: str, full_subcategory_of: tuple[Category, ...]) -> None:
        ...

    def name(self) -> str:
        ...

    def predicate(self) -> Predicate:
        ...

    def full_subcategory_of(self) -> tuple[Category, ...]:
        ...

    def intersection(self, other: PropertySubcategory[MorphismData, TwoMorphismData] | tuple[Category[MorphismData, TwoMorphismData], ...]) -> Category[MorphismData, TwoMorphismData]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__[Datum](self, *construction_data: Datum, **keywords: Datum) -> CategoryOfCategories.ElementType | Category[MorphismData, TwoMorphismData]:
        ...

class PredicateSubcategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData], metaclass=abc.ABCMeta):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> PredicateSubcategory.ObjectType:
            ...

        def codomain(self) -> PredicateSubcategory.ObjectType:
            ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], name: str, full_subcategory_of: tuple[Category, ...]) -> None:
        ...

class NarrowedProperty[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> NarrowedProperty.ObjectType:
            ...

        def codomain(self) -> NarrowedProperty.ObjectType:
            ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], roots: tuple[FullSubcategory, ...]) -> None:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def predicate(self) -> Predicate:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__[Datum](self, *construction_data: Datum, **keywords: Datum) -> CategoryOfCategories.ElementType:
        ...

class FixedEndpointProperty[**MorphismData, **TwoMorphismData](NarrowedProperty[TwoMorphismData, []]):

    class ObjectType(sage_categories.cat.properties.NarrowedProperty.ObjectType, sage_categories.cat.morphisms.IsomorphismsCategory.ObjectType, sage_categories.cat.morphisms.FixedEndpointCategory.ObjectType, sage_categories.cat.functors.FunctorCategory.MorphismType, sage_categories.cat.constructions.LimitsCategory.ElementType):
        ...

    class ElementType(sage_categories.cat.properties.NarrowedProperty.ElementType, sage_categories.cat.morphisms.IsomorphismsCategory.ElementType, sage_categories.cat.morphisms.FixedEndpointCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.properties.NarrowedProperty.MorphismType, sage_categories.cat.morphisms.IsomorphismsCategory.MorphismType, sage_categories.cat.morphisms.FixedEndpointCategory.MorphismType):
        ...

        def domain(self) -> FixedEndpointProperty.ObjectType:
            ...

        def codomain(self) -> FixedEndpointProperty.ObjectType:
            ...

    def domain(self) -> CategoryOfCategories.ElementType:
        ...

    def codomain(self) -> CategoryOfCategories.ElementType:
        ...

    def one(self) -> MorphismCategory.ObjectType:
        ...
