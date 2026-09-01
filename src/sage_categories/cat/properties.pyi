import sage_categories
import abc
from sage.misc.cachefunc import cached_method
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
__all__ = ['FullSubcategory', 'InverseImageSubcategory', 'inverse_image', 'PropertySubcategory', 'PredicateSubcategory', 'NarrowedProperty', 'FixedEndpointProperty']

class FullSubcategory[**MorphismData, **TwoMorphismData](Category[MorphismData, TwoMorphismData]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
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

class InverseImageSubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.morphisms.IsomorphismsCategory.ObjectType, sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.cat.functors.FunctorCategory.MorphismType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.cat.constructions.LimitsCategory.ElementType, sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.morphisms.IsomorphismsCategory.ElementType, sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.cat.morphisms.MorphismCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.IsomorphismsCategory.MorphismType, sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.cat.morphisms.MorphismCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory):
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

    @cached_method
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

def inverse_image(functor: Functor, target_subcategory: Category) -> Category:
    ...

class PropertySubcategory[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.ObjectOfCategory, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.cat.category.CategoryDeclaration):
        ...

    class ElementType(sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject, sage_categories.cat.morphisms.MorphismCategory.ElementType, sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.MorphismType, sage_categories.cat.category.CategoryOfCategories.MorphismType):
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

    @cached_method
    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, *arguments: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

class PredicateSubcategory[**MorphismData, **TwoMorphismData](PropertySubcategory[MorphismData, TwoMorphismData], metaclass=abc.ABCMeta):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[MorphismData, TwoMorphismData], name: str, full_subcategory_of: tuple[Category, ...]) -> None:
        ...

class NarrowedProperty[**MorphismData, **TwoMorphismData](FullSubcategory[MorphismData, TwoMorphismData]):

    class ObjectType(sage_categories.cat.morphisms.EndomorphismsCategory.ObjectType, sage_categories.cat.morphisms.IsomorphismsCategory.ObjectType, sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.morphisms.EndomorphismsCategory.ElementType, sage_categories.cat.morphisms.IsomorphismsCategory.ElementType, sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.EndomorphismsCategory.MorphismType, sage_categories.cat.morphisms.IsomorphismsCategory.MorphismType, sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory):
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

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

class FixedEndpointProperty[**MorphismData, **TwoMorphismData](NarrowedProperty[TwoMorphismData, []]):

    class ObjectType(sage_categories.cat.properties.InverseImageSubcategory.ObjectType, sage_categories.cat.morphisms.IsomorphismsCategory.ObjectType, sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.cat.morphisms.FixedEndpointCategory.ObjectType, sage_categories.cat.functors.FunctorCategory.MorphismType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.cat.constructions.LimitsCategory.ElementType, sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.properties.InverseImageSubcategory.ElementType, sage_categories.cat.morphisms.IsomorphismsCategory.ElementType, sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.cat.morphisms.FixedEndpointCategory.ElementType, sage_categories.cat.morphisms.MorphismCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.properties.InverseImageSubcategory.MorphismType, sage_categories.cat.morphisms.IsomorphismsCategory.MorphismType, sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.cat.morphisms.FixedEndpointCategory.MorphismType, sage_categories.cat.morphisms.MorphismCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory):
        ...

    def domain(self) -> CategoryOfCategories.ElementType:
        ...

    def codomain(self) -> CategoryOfCategories.ElementType:
        ...

    def __call__(self, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...

    def one(self) -> MorphismCategory.ObjectType:
        ...
