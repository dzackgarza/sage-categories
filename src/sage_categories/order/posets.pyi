import sage_categories.cat.properties
import sage_categories.order.posets
import sage_categories.sets.finite
from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Predicate, Proposition
from sage_categories.cat.properties import PropertySubcategory
__all__ = ['BinaryRelationsCategory', 'PosetsCategory', 'BinaryRelations', 'Posets', 'TotallyOrderedSets', 'Thin']
type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]

class _OrderRelatedPredicate(Predicate):
    name: str

class _PartialOrderPredicate(Predicate):
    name: str

class _TotalOrderPredicate(Predicate):
    name: str

class _StaticRoles_BinaryRelationsCategory:

    class ObjectType(sage_categories.sets.finite.SetsCategory.ObjectType):

        def __init__(self, relation: CategoryOfCategories.ElementType) -> None:
            ...

        def relation(self) -> CategoryOfCategories.ElementType:
            ...

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def related(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class ElementType(sage_categories.sets.finite.SetsCategory.ElementType):
        ...

    class MorphismType(sage_categories.sets.finite.SetsCategory.MorphismType):

        def __init__(self, underlying: MorphismCategory.ObjectType) -> None:
            ...

        def underlying_map(self) -> MorphismCategory.ObjectType:
            ...

        def domain(self) -> BinaryRelationsCategory.ObjectType:
            ...

        def codomain(self) -> BinaryRelationsCategory.ObjectType:
            ...

class BinaryRelationsCategory(_StaticRoles_BinaryRelationsCategory, Category[[MorphismCategory.ObjectType], [], _StaticRoles_BinaryRelationsCategory.ObjectType, _StaticRoles_BinaryRelationsCategory.ElementType, _StaticRoles_BinaryRelationsCategory.MorphismType]):
    PartialOrder: Incomplete

    def __call__(self, relation: CategoryOfCategories.ElementType) -> BinaryRelationsCategory.ObjectType:
        ...

    def from_predicate(self, carrier: CategoryOfCategories.ElementType, rule: OrderRule) -> BinaryRelationsCategory.ObjectType:
        ...

    def lift_order(self, diagram: Functor, presentation: LimitConesCategory.ObjectType) -> BinaryRelationsCategory.ObjectType:
        ...

    def transport(self, relation_object: BinaryRelationsCategory.ObjectType, bijection: MorphismCategory.ObjectType) -> BinaryRelationsCategory.MorphismType:
        ...

    def to_sets(self) -> Functor:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def construct_morphism(self, source: BinaryRelationsCategory.ObjectType, target: BinaryRelationsCategory.ObjectType, underlying: MorphismCategory.ObjectType) -> BinaryRelationsCategory.MorphismType:
        ...

    def construct_identity(self, relation_object: BinaryRelationsCategory.ObjectType) -> BinaryRelationsCategory.MorphismType:
        ...

    def composite(self, second: BinaryRelationsCategory.MorphismType, first: BinaryRelationsCategory.MorphismType) -> BinaryRelationsCategory.MorphismType:
        ...

class _StaticRoles_PosetsCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):

    class ObjectType(sage_categories.order.posets.BinaryRelationsCategory.ObjectType):
        ...

    class ElementType(sage_categories.order.posets.BinaryRelationsCategory.ElementType):

        def __le__(self, other: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class MorphismType(sage_categories.order.posets.BinaryRelationsCategory.MorphismType):
        ...

        def domain(self) -> PosetsCategory.ObjectType:
            ...

        def codomain(self) -> PosetsCategory.ObjectType:
            ...

class PosetsCategory(_StaticRoles_PosetsCategory, PropertySubcategory[[MorphismCategory.ObjectType], [], _StaticRoles_PosetsCategory.ObjectType, _StaticRoles_PosetsCategory.ElementType, _StaticRoles_PosetsCategory.MorphismType]):
    Total: Incomplete

def BinaryRelations() -> BinaryRelationsCategory:
    ...

def Posets() -> Category:
    ...

def TotallyOrderedSets() -> Category:
    ...
Thin: Functor
