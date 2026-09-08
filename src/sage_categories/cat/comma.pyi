import sage_categories
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['CommaCategory', 'comma_objects', 'CommaSpecialization']

@dataclass(frozen=True, eq=False)
class CommaObject:
    first: CategoryOfCategories.ElementType
    second: CategoryOfCategories.ElementType
    arrow: MorphismCategory.ObjectType

@dataclass(frozen=True, eq=False)
class CommaMorphism:
    first: MorphismCategory.ObjectType
    second: MorphismCategory.ObjectType

class CommaCategory(Category[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], []]):

    class ObjectType(sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: CommaObject) -> None:
            ...

        def first(self) -> CategoryOfCategories.ElementType:
            ...

        def second(self) -> CategoryOfCategories.ElementType:
            ...

        def arrow(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: CommaMorphism) -> None:
            ...

        def first(self) -> MorphismCategory.ObjectType:
            ...

        def second(self) -> MorphismCategory.ObjectType:
            ...

    def __init__(self, first: Functor, second: Functor) -> None:
        ...

    def comma_functors(self) -> tuple[Functor, Functor]:
        ...

    def from_arrow(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> CommaCategory.ObjectType:
        ...

    def morphism_from_pair(self, source: CommaCategory.ObjectType, target: CommaCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> CommaCategory.MorphismType:
        ...

    def construct_morphism(self, source: CommaCategory.ObjectType, target: CommaCategory.ObjectType, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> CommaCategory.MorphismType:
        ...

    def construct_identity(self, value: CommaCategory.ObjectType) -> CommaCategory.MorphismType:
        ...

    def composite(self, second: CommaCategory.MorphismType, first: CommaCategory.MorphismType) -> CommaCategory.MorphismType:
        ...

    @cached_method
    def first_projection(self) -> Functor:
        ...

    @cached_method
    def second_projection(self) -> Functor:
        ...

    @cached_method
    def defining_transformation(self) -> NaturalTransformation:
        ...

    @cached_method
    def arrow_projection(self) -> Functor:
        ...

    @cached_method
    def pair_projection(self) -> Functor:
        ...

def comma_objects(first: Functor, second: Functor) -> CommaCategory:
    ...

class CommaSpecialization(CommaCategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...
