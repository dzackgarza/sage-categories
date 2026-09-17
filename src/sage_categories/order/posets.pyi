from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.cat.category import Category as Category, CategoryOfCategories as CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory as LimitConesCategory
from sage_categories.cat.declarations import Sets as Sets
from sage_categories.cat.functors import Cat as Cat, Fun as Fun, Functor as Functor
from sage_categories.cat.morphisms import Mor as Mor, MorphismCategory as MorphismCategory
from sage_categories.cat.predicates import Axiom as Axiom, Predicate as Predicate, Proposition as Proposition, conjunction as conjunction, register_handler as register_handler
from sage_categories.cat.properties import PropertySubcategory as PropertySubcategory
from sage_categories.cat.shapes import Discrete as Discrete, ThinCategory as ThinCategory
from sage_categories.kernel.sage_runtime import cached_function as cached_function, cached_method as cached_method
type OrderRule = Callable[[CategoryOfCategories.ElementType, CategoryOfCategories.ElementType], Proposition]

class BinaryRelationsCategory(Category[[MorphismCategory.ObjectType], []]):

    class ObjectType:

        def __init__(self, relation: CategoryOfCategories.ElementType) -> None:
            ...

        def relation(self) -> CategoryOfCategories.ElementType:
            ...

        def carrier(self) -> CategoryOfCategories.ElementType:
            ...

        def related(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class ElementType:
        ...

    class MorphismType:

        def __init__(self, underlying: MorphismCategory.ObjectType) -> None:
            ...

        def underlying_map(self) -> MorphismCategory.ObjectType:
            ...
    PartialOrder: Incomplete

    def __call__(self, relation: CategoryOfCategories.ElementType) -> BinaryRelationsCategory.ObjectType:
        ...

    def from_predicate(self, carrier: CategoryOfCategories.ElementType, rule: OrderRule) -> BinaryRelationsCategory.ObjectType:
        ...

    def lift_order(self, diagram: Functor, presentation: LimitConesCategory.ObjectType) -> BinaryRelationsCategory.ObjectType:
        ...

    def transport(self, relation_object: BinaryRelationsCategory.ObjectType, bijection: MorphismCategory.ObjectType) -> BinaryRelationsCategory.MorphismType:
        ...

    @cached_method
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

class PosetsCategory(PropertySubcategory[[MorphismCategory.ObjectType], []]):

    class ObjectType:
        ...

    class ElementType:

        def __le__(self, other: CategoryOfCategories.ElementType) -> Proposition:
            ...

    class MorphismType:
        ...
    Total: Incomplete

def BinaryRelations() -> BinaryRelationsCategory:
    ...

def Posets() -> Category:
    ...

def TotallyOrderedSets() -> Category:
    ...
Thin: Functor
