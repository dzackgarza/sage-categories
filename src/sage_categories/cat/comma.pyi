import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
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

class _StaticRoles_CommaCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, data: CommaObject) -> None:
            ...

        def first(self) -> CategoryOfCategories.ElementType:
            ...

        def second(self) -> CategoryOfCategories.ElementType:
            ...

        def arrow(self) -> MorphismCategory.ObjectType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: CommaMorphism) -> None:
            ...

        def first(self) -> MorphismCategory.ObjectType:
            ...

        def second(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> CommaCategory.ObjectType:
            ...

        def codomain(self) -> CommaCategory.ObjectType:
            ...

class CommaCategory[_ObjectRole = _StaticRoles_CommaCategory.ObjectType, _ElementRole = _StaticRoles_CommaCategory.ElementType, _MorphismRole = _StaticRoles_CommaCategory.MorphismType](_StaticRoles_CommaCategory, Category[[MorphismCategory.ObjectType, MorphismCategory.ObjectType], [], _ObjectRole, _ElementRole, _MorphismRole]):

    def __init__(self, first: Functor, second: Functor) -> None:
        ...

    def comma_functors(self) -> tuple[Functor, Functor]:
        ...

    def from_arrow(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType, arrow: MorphismCategory.ObjectType) -> _ObjectRole:
        ...

    def morphism_from_pair(self, source: _ObjectRole, target: _ObjectRole, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> _MorphismRole:
        ...

    def construct_morphism(self, source: _ObjectRole, target: _ObjectRole, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> _MorphismRole:
        ...

    def construct_identity(self, value: _ObjectRole) -> _MorphismRole:
        ...

    def composite(self, second: _MorphismRole, first: _MorphismRole) -> _MorphismRole:
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

class _StaticRoles_CommaSpecialization(_StaticRoles_CommaCategory):

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):
        ...

        def domain(self) -> CommaSpecialization.ObjectType:
            ...

        def codomain(self) -> CommaSpecialization.ObjectType:
            ...

class CommaSpecialization(_StaticRoles_CommaSpecialization, CommaCategory[_StaticRoles_CommaSpecialization.ObjectType, _StaticRoles_CommaSpecialization.ElementType, _StaticRoles_CommaSpecialization.MorphismType]):

    def structure_functors(self) -> tuple[Functor, ...]:
        ...
