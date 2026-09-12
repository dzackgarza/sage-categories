from collections.abc import Callable

from _typeshed import Incomplete

import sage_categories.cat.properties
import sage_categories.sets.finite
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.category import Category as Category
from sage_categories.cat.category import CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory as LimitConesCategory
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.functors import Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.morphisms import MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Axiom as Axiom
from sage_categories.cat.predicates import Predicate as Predicate
from sage_categories.cat.predicates import Proposition as Proposition
from sage_categories.cat.predicates import conjunction as conjunction
from sage_categories.cat.predicates import register_handler as register_handler
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.cat.shapes import Discrete as Discrete
from sage_categories.cat.shapes import ThinCategory as ThinCategory
from sage_categories.kernel.sage_runtime import cached_function as cached_function

__all__ = ["BinaryRelations", "BinaryRelationsCategory", "Posets", "PosetsCategory", "Thin", "TotallyOrderedSets"]
type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]

class _StaticRoles_BinaryRelationsCategory:
    class ObjectType(sage_categories.sets.finite._StaticRoles_SetsCategory.ObjectType):
        def __init__(self, relation: CategoryOfCategories.ElementType) -> None: ...
        def relation(self) -> CategoryOfCategories.ElementType: ...
        def carrier(self) -> CategoryOfCategories.ElementType: ...
        def related(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> Proposition: ...

    class ElementType(sage_categories.sets.finite._StaticRoles_SetsCategory.ElementType): ...

    class MorphismType(sage_categories.sets.finite._StaticRoles_SetsCategory.MorphismType):
        def __init__(self, underlying: MorphismCategory.ObjectType) -> None: ...
        def underlying_map(self) -> MorphismCategory.ObjectType: ...
        def domain(self) -> BinaryRelationsCategory.ObjectType: ...
        def codomain(self) -> BinaryRelationsCategory.ObjectType: ...

class BinaryRelationsCategory(
    _StaticRoles_BinaryRelationsCategory,
    Category[
        [MorphismCategory.ObjectType],
        [],
        _StaticRoles_BinaryRelationsCategory.ObjectType,
        _StaticRoles_BinaryRelationsCategory.ElementType,
        _StaticRoles_BinaryRelationsCategory.MorphismType,
    ],
):
    PartialOrder: Incomplete

    def __call__(self, relation: CategoryOfCategories.ElementType) -> BinaryRelationsCategory.ObjectType: ...
    def from_predicate(self, carrier: CategoryOfCategories.ElementType, rule: OrderRule) -> BinaryRelationsCategory.ObjectType: ...
    def lift_order(self, diagram: Functor, presentation: LimitConesCategory.ObjectType) -> BinaryRelationsCategory.ObjectType: ...
    def transport(self, relation_object: BinaryRelationsCategory.ObjectType, bijection: MorphismCategory.ObjectType) -> BinaryRelationsCategory.MorphismType: ...
    def to_sets(self) -> Functor: ...
    def structure_functors(self) -> tuple[Functor, ...]: ...
    def construct_morphism(
        self, source: BinaryRelationsCategory.ObjectType, target: BinaryRelationsCategory.ObjectType, underlying: MorphismCategory.ObjectType
    ) -> BinaryRelationsCategory.MorphismType: ...
    def construct_identity(self, relation_object: BinaryRelationsCategory.ObjectType) -> BinaryRelationsCategory.MorphismType: ...
    def composite(self, second: BinaryRelationsCategory.MorphismType, first: BinaryRelationsCategory.MorphismType) -> BinaryRelationsCategory.MorphismType: ...

class _StaticRoles_PosetsCategory(sage_categories.cat.properties._StaticRoles_PropertySubcategory):
    class ObjectType(_StaticRoles_BinaryRelationsCategory.ObjectType): ...

    class ElementType(_StaticRoles_BinaryRelationsCategory.ElementType):
        def __le__(self, other: CategoryOfCategories.ElementType) -> Proposition: ...

    class MorphismType(_StaticRoles_BinaryRelationsCategory.MorphismType):
        def domain(self) -> PosetsCategory.ObjectType: ...
        def codomain(self) -> PosetsCategory.ObjectType: ...

class PosetsCategory(
    _StaticRoles_PosetsCategory,
    PropertySubcategory[
        [MorphismCategory.ObjectType], [], _StaticRoles_PosetsCategory.ObjectType, _StaticRoles_PosetsCategory.ElementType, _StaticRoles_PosetsCategory.MorphismType
    ],
):
    Total: Incomplete

def BinaryRelations() -> BinaryRelationsCategory: ...
def Posets() -> Category: ...
def TotallyOrderedSets() -> Category: ...

Thin: Functor
