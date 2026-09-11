import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from collections.abc import Callable
from dataclasses import dataclass
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Proposition, UnknownClass
from sage_categories.kernel.retention import retained_involution
from sage_categories.kernel.roles import Role
__all__ = ['OppositeCategory', 'opposite_category', 'opposite_morphism', 'Op', 'opposite_functor', 'opposite_transformation', 'op_squared_isomorphism']

@dataclass(frozen=True, eq=False, slots=True)
class _OppositeMorphismData:
    original: MorphismCategory.ObjectType

class _StaticRoles_OppositeCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):
        ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: _OppositeMorphismData) -> None:
            ...

        def original(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> OppositeCategory.ObjectType:
            ...

        def codomain(self) -> OppositeCategory.ObjectType:
            ...

class OppositeCategory[**MorphismData, **TwoMorphismData](_StaticRoles_OppositeCategory, Category[[MorphismCategory.ObjectType], [], _StaticRoles_OppositeCategory.ObjectType, _StaticRoles_OppositeCategory.ElementType, _StaticRoles_OppositeCategory.MorphismType]):

    def __init__(self, original: Category[MorphismData, TwoMorphismData]) -> None:
        ...

    def original(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def is_discrete(self) -> bool:
        ...

    def role_source(self, role: Role) -> tuple[Category, Role]:
        ...

    def narrowing_base(self) -> Category:
        ...

    def narrowing_roots(self) -> tuple[Category, ...]:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_point(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def generating_morphisms(self) -> tuple[MorphismCategory.ObjectType, ...] | UnknownClass:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, original: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def colimit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

def opposite_category(category: Category) -> Category:
    ...

def opposite_morphism(morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    ...
Op: Functor

def opposite_functor(functor: Functor) -> Functor:
    ...

@retained_involution
def opposite_transformation(transformation: NaturalTransformation) -> NaturalTransformation:
    ...

def op_squared_isomorphism() -> NaturalTransformation:
    ...
