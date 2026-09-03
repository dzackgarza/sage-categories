import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject, Proposition
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory
from sage_categories.cat.properties import FixedEndpointProperty, PropertySubcategory
__all__ = ['Functor', 'FunctorProperty', 'FunctorCategory', 'FunctorsCategory', 'Fun', 'NaturalTransformation']

@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    assignment: Assignment
Cat = _category.Cat
Functor: Incomplete

class FunctorProperties:

    def Full(self) -> Category:
        ...

    def Faithful(self) -> Category:
        ...

    def FullyFaithful(self) -> Category:
        ...

    def EssentiallySurjective(self) -> Category:
        ...

    def Equivalences(self) -> Category:
        ...

    def PreservesLimits(self, shape: Category) -> Category:
        ...

    def CreatesLimits(self, shape: Category) -> Category:
        ...

    def Isofibrations(self) -> Category:
        ...

    def Monomorphisms(self) -> Category:
        ...

class ShapeIndexedFunctorProperty(FunctorProperties, PropertySubcategory[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType:
        ...

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: FunctorCategory, property_name: str, shape: Category) -> None:
        ...

    def shape(self) -> Category:
        ...

    def narrowing_type(self) -> type[FunctorProperty]:
        ...

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        ...

class FunctorProperty(FunctorProperties, FixedEndpointProperty[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType(sage_categories.cat.functors.FunctorCategory.ObjectType, sage_categories.cat.morphisms.IsomorphismsCategory.ObjectType, sage_categories.cat.properties.PropertySubcategory.ObjectType, sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.ObjectOfCategory, sage_categories.cat.properties.NarrowedProperty.ObjectType, sage_categories.cat.morphisms.EndomorphismsCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.functors.FunctorCategory.ElementType, sage_categories.cat.morphisms.IsomorphismsCategory.ElementType, sage_categories.cat.properties.PropertySubcategory.ElementType, sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject, sage_categories.cat.properties.NarrowedProperty.ElementType, sage_categories.cat.morphisms.EndomorphismsCategory.ElementType):
        ...

    class MorphismType(sage_categories.cat.functors.FunctorCategory.MorphismType, sage_categories.cat.morphisms.IsomorphismsCategory.MorphismType, sage_categories.cat.properties.PropertySubcategory.MorphismType, sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.properties.NarrowedProperty.MorphismType, sage_categories.cat.morphisms.EndomorphismsCategory.MorphismType):
        ...

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        ...

class FunctorCategory(FunctorProperties, FixedEndpointCategory[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory):
        ...

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        ...

    def PreservesLimits(self, shape: Category) -> Category:
        ...

    def CreatesLimits(self, shape: Category) -> Category:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def diagram(self, value: CategoryOfCategories.ElementType) -> Functor:
        ...

    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, assignment: Assignment) -> NaturalTransformation:
        ...

    def evaluation(self, vertex: CategoryOfCategories.ElementType) -> Functor:
        ...

    def constant(self, value: CategoryOfCategories.ElementType) -> Functor:
        ...

    def diagonal(self) -> Functor:
        ...

    def TotalCones(self) -> Category:
        ...

    def has_constant_value(self, diagram: Functor) -> bool:
        ...

    def constant_value(self, diagram: Functor) -> CategoryOfCategories.ElementType:
        ...

    def from_object_rule(self, rule: OnObject) -> Functor:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> NaturalTransformation:
        ...

    def narrowing_type(self) -> type[FunctorProperty]:
        ...

class FunctorsCategory(MorphismCategory[[OnObject, OnMorphism], [Assignment]]):
    ObjectType = CategoryOfCategories.MorphismType

    class ElementType(sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory):

        def __init__(self, data: NaturalTransformationData) -> None:
            ...

        def source_functor(self) -> Functor:
            ...

        def target_functor(self) -> Functor:
            ...

        def component(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

        def op(self) -> NaturalTransformation:
            ...

        def whisker_left(self, functor: Functor) -> NaturalTransformation:
            ...

        def whisker_right(self, functor: Functor) -> NaturalTransformation:
            ...

        def horizontal(self, transformation: NaturalTransformation) -> NaturalTransformation:
            ...

    def __init__(self, base: CategoryOfCategories) -> None:
        ...

    def fixed_endpoint_type(self) -> type[FunctorCategory]:
        ...

    def __call__(self, shape: Category, target: Category | Functor) -> FunctorCategory | Functor:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...
    Full: Incomplete
    Faithful: Incomplete
    EssentiallySurjective: Incomplete
    FullyFaithful: Incomplete
    Equivalences: Incomplete

    def Isofibrations(self) -> Category:
        ...

    def Monomorphisms(self) -> Category:
        ...

    def declares_inheritance(self, functor: Functor) -> bool:
        ...

    def declares_subcategory(self, functor: Functor) -> bool:
        ...

    def subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        ...

    def full_subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...
Fun: FunctorsCategory
NaturalTransformation: Incomplete
