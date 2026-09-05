import sage_categories
from _typeshed import Incomplete
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.comma import CommaSpecialization
from sage_categories.cat.cones import ConeCategory
from sage_categories.cat.functors import Functor, FunctorCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['TotalConesCategory', 'TotalLimitConesCategory', 'total_cones']

class TotalConesCategory(CommaSpecialization):
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

class TotalLimitConesCategory(PropertySubcategory[[MorphismCategory.ObjectType, NaturalTransformation], []]):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

def total_cones(diagrams: FunctorCategory) -> TotalConesCategory:
    ...
