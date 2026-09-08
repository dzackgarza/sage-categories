import sage_categories
from sage_categories.cat.cat_constructions import LimitSubcategory
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['InserterCategory', 'Inserter', 'EquifierCategory', 'Equifier', 'Algebras', 'Magmas', 'PointedMagmas', 'Monoids', 'EilenbergMoore']

class InserterCategory(LimitSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def structure(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def underlying_morphism(self) -> MorphismCategory.ObjectType:
            ...

    def algebra(self, carrier: CategoryOfCategories.ElementType, structure: MorphismCategory.ObjectType) -> InserterCategory.ObjectType:
        ...

    def homomorphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> InserterCategory.MorphismType:
        ...

    @cached_method
    def forgetful(self) -> Functor:
        ...

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        ...

def Inserter(first: Functor, second: Functor) -> InserterCategory:
    ...

class EquifierCategory(FullSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __init__(self, first: NaturalTransformation, second: NaturalTransformation) -> None:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

def Equifier(first: NaturalTransformation, second: NaturalTransformation) -> EquifierCategory:
    ...

def Algebras(endofunctor: Functor) -> InserterCategory:
    ...

def Magmas(tensor: Functor) -> InserterCategory:
    ...

def PointedMagmas(tensor: Functor, unit: CategoryOfCategories.ElementType) -> InserterCategory:
    ...

def Monoids(base: Category) -> EquifierCategory:
    ...

def EilenbergMoore(endofunctor: Functor, unit: NaturalTransformation, multiplication: NaturalTransformation) -> EquifierCategory:
    ...
