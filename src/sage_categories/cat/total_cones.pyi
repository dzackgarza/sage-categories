import sage_categories
from _typeshed import Incomplete
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import ConeCategory
from sage_categories.cat.functors import Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.cat.slices import CommaCategory
__all__ = ['TotalConesCategory', 'TotalLimitConesCategory', 'total_cones']

@dataclass(frozen=True, eq=False, slots=True)
class TotalConeMorphismData:
    apex: MorphismCategory.ObjectType
    diagram: NaturalTransformation

class TotalConesCategory(CommaCategory):
    LimitCones: Incomplete

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def presentation(self) -> ConeCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def apex_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def diagram_transformation(self) -> NaturalTransformation:
            ...

    def __init__(self, defining_diagram: Functor, diagrams: FunctorCategory, diagonal: Functor, identity: Functor) -> None:
        ...

    def diagrams(self) -> FunctorCategory:
        ...

    def diagonal_functor(self) -> Functor:
        ...

    def identity_functor(self) -> Functor:
        ...

    def diagram_projection(self) -> Functor:
        ...

    def apex_functor(self) -> Functor:
        ...

    def apex_fiber(self, apex: CategoryOfCategories.ElementType) -> Category:
        ...

    def __call__(self, presentation: ConeCategory.ObjectType) -> TotalConesCategory.ObjectType:
        ...

    def construct_morphism(self, source: TotalConesCategory.ObjectType, target: TotalConesCategory.ObjectType, apex: MorphismCategory.ObjectType, diagram: NaturalTransformation) -> TotalConesCategory.MorphismType:
        ...

    def construct_identity(self, member_object: TotalConesCategory.ObjectType) -> TotalConesCategory.MorphismType:
        ...

    def composite(self, second: TotalConesCategory.MorphismType, first: TotalConesCategory.MorphismType) -> TotalConesCategory.MorphismType:
        ...

class TotalLimitConesCategory(PropertySubcategory[[MorphismCategory.ObjectType, NaturalTransformation], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

def total_cones(diagrams: FunctorCategory) -> TotalConesCategory:
    ...
