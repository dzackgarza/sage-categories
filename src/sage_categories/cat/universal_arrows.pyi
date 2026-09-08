import sage_categories
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.properties import FullSubcategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['TerminalObjectsCategory', 'TerminalObjects', 'InitialObjectsCategory', 'InitialObjects', 'RightUniversalArrows', 'LeftUniversalArrows', 'right_mate', 'left_mate']
type Factor = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
type Choice = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]

class TerminalObjectsCategory(FullSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def unique_from(self, source: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __call__(self, value: CategoryOfCategories.ElementType, factor: Factor) -> CategoryOfCategories.ElementType:
        ...

def TerminalObjects(category: Category) -> TerminalObjectsCategory:
    ...

class InitialObjectsCategory(FullSubcategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):

        def unique_to(self, target: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def __call__(self, value: CategoryOfCategories.ElementType, factor: Factor) -> CategoryOfCategories.ElementType:
        ...

def InitialObjects(category: Category) -> InitialObjectsCategory:
    ...

@dataclass(eq=False)
class RightUniversalArrows:
    forward: Functor
    choose: Choice

    def presentation(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def factor(self, target: CategoryOfCategories.ElementType, source: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    @cached_method
    def functor(self) -> Functor:
        ...

    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType:
        ...

@dataclass(eq=False)
class LeftUniversalArrows:
    inverse: Functor
    choose: Choice

    def presentation(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def factor(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    @cached_method
    def functor(self) -> Functor:
        ...

    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType:
        ...

def right_mate(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, top: Functor, bottom: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    ...

def left_mate(first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, top: Functor, bottom: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
    ...
