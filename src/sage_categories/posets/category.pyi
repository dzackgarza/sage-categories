from _typeshed import Incomplete
from dataclasses import dataclass, field
from sage.misc.cachefunc import cached_method
from sage.structure.coerce_dict import MonoDict
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import AppliedPredicate, Decision, Proposition
from sage_categories.cat.shapes import ThinCategory
from sage_categories.sets.category import SetMap
from sage_categories.sets.category import SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule
from sage_categories.sets.category import SetObject
__all__ = ['PosetsCategory', 'Poset', 'PosetElement', 'MonotoneMap', 'Posets', 'FinitePosets', 'TotallyOrderedSets', 'FiniteTotallyOrderedSets']
type Relation = dict[tuple[int, int], Decision]

@dataclass(eq=False, slots=True)
class PosetObjectData:
    relation: SetObject
    elements: MonoDict = field(default_factory=MonoDict)

@dataclass(frozen=True, eq=False, slots=True)
class PosetMorphismData:
    set_map: SetMap

class PosetDeclaration:

    def __init__(self, data: PosetObjectData) -> None:
        ...

    def relation(self) -> SetObject:
        ...

    def element(self, point: SetElement) -> PosetElement:
        ...

    def sub_poset(self, predicate: MembershipRule) -> Poset:
        ...

    def is_total(self) -> AppliedPredicate:
        ...

    def thin_category(self) -> ThinCategory:
        ...

class PosetElementDeclaration:

    def __le__(self, other: PosetElement) -> AppliedPredicate:
        ...

    def __lt__(self, other: PosetElement) -> Proposition:
        ...

    def __ge__(self, other: PosetElement) -> AppliedPredicate:
        ...

    def __gt__(self, other: PosetElement) -> Proposition:
        ...

class MonotoneMapDeclaration:
    ...

class PosetsCategory(Category[[Rule], []]):
    ObjectType = PosetDeclaration
    ElementType = PosetElementDeclaration
    MorphismType = MonotoneMapDeclaration

    def __init__(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    @cached_method
    def underlying_set_functor(self) -> Functor:
        ...

    def __call__(self, relation: SetObject) -> Poset:
        ...

    def carrier(self, relation: SetObject) -> SetObject:
        ...

    def is_partial_order(self, relation: SetObject) -> AppliedPredicate:
        ...

    def is_order_preserving(self, source: Poset, target: Poset, set_map: SetMap) -> AppliedPredicate:
        ...

    @cached_method
    def Simplex(self, dimension: int) -> Poset:
        ...

    @cached_method
    def Terminal(self) -> Poset:
        ...

    def subset_poset(self, base_set: SetObject) -> Poset:
        ...

    @cached_method
    def Finite(self) -> Category[[Rule], []]:
        ...

    def TotallyOrdered(self) -> Category[[Rule], []]:
        ...

    def element_from_defining_morphism(self, defining_morphism: MonotoneMap) -> PosetElement:
        ...

    def construct_morphism(self, domain: Poset, codomain: Poset, rule: Rule) -> MonotoneMap:
        ...

    def construct_identity(self, poset: Poset) -> MonotoneMap:
        ...

    def composite(self, second: MonotoneMap, first: MonotoneMap) -> MonotoneMap:
        ...

    def inverse_morphism(self, monotone: MonotoneMap) -> MonotoneMap:
        ...
Poset: Incomplete
PosetElement: Incomplete
MonotoneMap: Incomplete

def Posets() -> PosetsCategory:
    ...

def FinitePosets() -> Category[[Rule], []]:
    ...

def TotallyOrderedSets() -> Category[[Rule], []]:
    ...

def FiniteTotallyOrderedSets() -> Category[[Rule], []]:
    ...
