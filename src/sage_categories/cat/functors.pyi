import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat import category as _category
from sage_categories.cat.category import Assignment, Category, CategoryOfCategories, OnMorphism, OnObject, Predicate, Proposition
from sage_categories.cat.morphisms import FixedEndpointCategory, MorphismCategory
from sage_categories.cat.properties import FixedEndpointProperty, PropertySubcategory
__all__ = ['Functor', 'FunctorProperty', 'FunctorCategory', 'FunctorsCategory', 'PreservesLimitsCategory', 'CreatesLimitsCategory', 'Fun', 'NaturalTransformation']

@dataclass(frozen=True, eq=False, slots=True)
class NaturalTransformationData:
    assignment: Assignment
    source: Functor
    target: Functor
Cat = _category.Cat
Functor: Incomplete

class ShapeIndexedFunctorProperty(PropertySubcategory[[OnObject, OnMorphism], [Assignment]]):

    def __init__(self, ambient: FunctorsCategory, name: str, full_subcategory_of: tuple[Category, ...], shape: Category | Functor) -> None:
        ...

    def shape(self) -> Category | Functor:
        ...

class FunctorProperty(FixedEndpointProperty[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __call__(self, *args: OnObject | OnMorphism, **kwargs: OnObject | OnMorphism) -> Functor:
        ...

class _DenotesDiagramPredicate(Predicate):
    name: str

class _DenotesFunctorPredicate(Predicate):
    name: str

class FunctorCategory(FixedEndpointCategory[[OnObject, OnMorphism], [Assignment]]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    class ElementType(sage_categories.cat.functors.FunctorsCategory.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.functors.FunctorsCategory.MorphismType, sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, morphisms: MorphismCategory, domain: Category, codomain: Category) -> None:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def diagram(self, value: CategoryOfCategories.ElementType) -> Functor:
        ...

    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, assignment: Assignment) -> NaturalTransformation:
        ...

    def construct_identity(self, value: CategoryOfCategories.ElementType) -> NaturalTransformation:
        ...

    def evaluation(self, vertex: CategoryOfCategories.ElementType) -> Functor:
        ...

    def ev(self, vertex: CategoryOfCategories.ElementType | int) -> Functor:
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

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):

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
    Isofibrations: Incomplete
    Monomorphisms: Incomplete
    Fibrations: Incomplete
    Opfibrations: Incomplete
    PreservesLimits: Incomplete
    CreatesLimits: Incomplete

    def identity_on_values(self, source: Category, target: Category) -> Functor:
        ...

    def declares_inheritance(self, functor: Functor) -> bool:
        ...

    def declares_subcategory(self, functor: Functor) -> bool:
        ...

    def declares_point(self, functor: Functor) -> bool:
        ...

    def subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        ...

    def full_subcategory_monomorphism(self, source: Category, target: Category) -> Functor:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

class PreservesLimitsCategory(ShapeIndexedFunctorProperty):
    ...

class CreatesLimitsCategory(ShapeIndexedFunctorProperty):
    ...
Fun: FunctorsCategory
NaturalTransformation: Incomplete
