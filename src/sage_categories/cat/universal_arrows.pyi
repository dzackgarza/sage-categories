from collections.abc import Callable
from dataclasses import dataclass

import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.cat.properties
import sage_categories.kernel.roles
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.comma import comma_objects as comma_objects
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.functors import NaturalTransformation as NaturalTransformation
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.properties import FullSubcategory as FullSubcategory
from sage_categories.kernel.refinement import refine as refine
from sage_categories.kernel.retention import identity_key as identity_key
from sage_categories.kernel.sage_runtime import cached_function as cached_function
from sage_categories.kernel.sage_runtime import cached_method as cached_method

__all__ = ["InitialObjects", "InitialObjectsCategory", "LeftUniversalArrows", "RightUniversalArrows", "TerminalObjects", "TerminalObjectsCategory", "left_mate", "right_mate"]
type Factor = Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType]
type Choice = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]

class _StaticRoles_TerminalObjectsCategory(sage_categories.cat.properties._StaticRoles_FullSubcategory):
    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def unique_from(self, source: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> TerminalObjectsCategory.ObjectType: ...
        def codomain(self) -> TerminalObjectsCategory.ObjectType: ...

class TerminalObjectsCategory(
    _StaticRoles_TerminalObjectsCategory,
    FullSubcategory[
        ..., ..., _StaticRoles_TerminalObjectsCategory.ObjectType, _StaticRoles_TerminalObjectsCategory.ElementType, _StaticRoles_TerminalObjectsCategory.MorphismType
    ],
):
    def __call__(self, value: CategoryOfCategories.ElementType, factor: Factor) -> CategoryOfCategories.ElementType: ...

def TerminalObjects(category: Category) -> TerminalObjectsCategory: ...

class _StaticRoles_InitialObjectsCategory(sage_categories.cat.properties._StaticRoles_FullSubcategory):
    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        def unique_to(self, target: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType: ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject): ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> InitialObjectsCategory.ObjectType: ...
        def codomain(self) -> InitialObjectsCategory.ObjectType: ...

class InitialObjectsCategory(
    _StaticRoles_InitialObjectsCategory,
    FullSubcategory[
        ..., ..., _StaticRoles_InitialObjectsCategory.ObjectType, _StaticRoles_InitialObjectsCategory.ElementType, _StaticRoles_InitialObjectsCategory.MorphismType
    ],
):
    def __call__(self, value: CategoryOfCategories.ElementType, factor: Factor) -> CategoryOfCategories.ElementType: ...

def InitialObjects(category: Category) -> InitialObjectsCategory: ...

@dataclass(eq=False)
class RightUniversalArrows:
    forward: Functor
    choose: Choice

    def presentation(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
    def factor(self, target: CategoryOfCategories.ElementType, source: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
    @cached_method
    def functor(self) -> Functor: ...
    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType: ...

@dataclass(eq=False)
class LeftUniversalArrows:
    inverse: Functor
    choose: Choice

    def presentation(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType: ...
    def factor(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType: ...
    @cached_method
    def functor(self) -> Functor: ...
    @cached_method
    def adjunction(self) -> CategoryOfCategories.ElementType: ...

def right_mate(
    first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, top: Functor, bottom: Functor, transformation: NaturalTransformation
) -> NaturalTransformation: ...
def left_mate(
    first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, top: Functor, bottom: Functor, transformation: NaturalTransformation
) -> NaturalTransformation: ...
