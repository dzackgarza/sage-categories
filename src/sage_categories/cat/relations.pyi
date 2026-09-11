import sage_categories.cat.category
import sage_categories.cat.morphisms
import sage_categories.kernel.roles
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
from sage_categories.kernel.sage_runtime import cached_method
__all__ = ['relation_inclusion', 'RelationsCategory', 'RelationMorphismsCategory', 'Relations']

class _RelationInclusion(Predicate):
    name: str
relation_inclusion: Predicate

class _StaticRoles_RelationsCategory:

    class ObjectType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ObjectOfCategory):

        def __init__(self, carrier: CategoryOfCategories.ElementType) -> None:
            ...

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, subobject: CategoryOfCategories.ElementType) -> None:
            ...

        def subobject(self) -> CategoryOfCategories.ElementType:
            ...

        def monomorphism(self) -> MorphismCategory.ObjectType:
            ...

        def left(self) -> MorphismCategory.ObjectType:
            ...

        def right(self) -> MorphismCategory.ObjectType:
            ...

        def converse(self) -> MorphismCategory.ObjectType:
            ...

        def leq(self, other: MorphismCategory.ObjectType) -> Proposition:
            ...

        def is_reflexive(self) -> Proposition:
            ...

        def is_transitive(self) -> Proposition:
            ...

        def is_antisymmetric(self) -> Proposition:
            ...

        def domain(self) -> RelationsCategory.ObjectType:
            ...

        def codomain(self) -> RelationsCategory.ObjectType:
            ...

class RelationsCategory(_StaticRoles_RelationsCategory, Category[[MorphismCategory.ObjectType], [MorphismCategory.ObjectType], _StaticRoles_RelationsCategory.ObjectType, _StaticRoles_RelationsCategory.ElementType, _StaticRoles_RelationsCategory.MorphismType]):

    def __init__(self, base: Category) -> None:
        ...

    def regular_category(self) -> Category:
        ...

    def __call__(self, carrier: CategoryOfCategories.ElementType) -> RelationsCategory.ObjectType:
        ...

    def morphism_category_type(self) -> type[RelationMorphismsCategory]:
        ...

    def construct_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, mono: MorphismCategory.ObjectType) -> RelationsCategory.MorphismType:
        ...

    def graph(self, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, value: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def meet(self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_two_morphism(self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType, factor: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def identity_two_morphism(self, arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def compose_two_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def inclusion(self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def horizontal_composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def associator(self, third: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    @cached_method
    def graph_functor(self) -> Functor:
        ...

class _StaticRoles_RelationMorphismsCategory(sage_categories.cat.morphisms._StaticRoles_MorphismCategory):

    class ElementType(sage_categories.cat.category.CategoryOfCategories.ElementType, sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, factor: MorphismCategory.ObjectType) -> None:
            ...

        def factor(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> RelationMorphismsCategory.ObjectType:
            ...

        def codomain(self) -> RelationMorphismsCategory.ObjectType:
            ...

class RelationMorphismsCategory(_StaticRoles_RelationMorphismsCategory, MorphismCategory[..., ..., RelationsCategory.MorphismType, _StaticRoles_RelationMorphismsCategory.ElementType, _StaticRoles_RelationMorphismsCategory.MorphismType]):
    ObjectType = RelationsCategory.MorphismType

def Relations(base: Category) -> RelationsCategory:
    ...
