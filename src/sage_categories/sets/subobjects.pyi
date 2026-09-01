from collections.abc import Callable
from sage_categories.cat.category import Category
from sage_categories.cat.predicates import AppliedPredicate, Predicate
from sage_categories.cat.properties import FullSubcategory
from sage_categories.cat.slices import SliceLikeCategory, SliceProperty
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.category import SetMap
from sage_categories.sets.elements import Datum
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule
from sage_categories.sets.category import SetObject
__all__ = ['SetSubobjects', 'subset_of', 'ChosenSubsetsCategory', 'ChosenQuotientsCategory']

class SetSubobjects(SliceProperty):

    class ElementType:
        ...

    class MorphismType:
        ...

    class ObjectType:
        ...

    def from_predicate(self, predicate: MembershipRule) -> SliceLikeCategory.ObjectType:
        ...
subset_of: Predicate

class ChosenSubsetObject:

    def monomorphism(self) -> SetMap:
        ...

    def underlying_set(self) -> SetObject:
        ...

    def characteristic_morphism(self) -> SetMap:
        ...

    def __le__(self, other: SetObject) -> AppliedPredicate:
        ...

    def union(self, other: SetObject) -> SetObject:
        ...

    def intersection(self, other: SetObject) -> SetObject:
        ...

    def difference(self, other: SetObject) -> SetObject:
        ...

    def symmetric_difference(self, other: SetObject) -> SetObject:
        ...

    def complement(self) -> SetObject:
        ...

    def __or__(self, other: SetObject) -> SetObject:
        ...

    def __and__(self, other: SetObject) -> SetObject:
        ...

class ChosenSubsetsCategory(FullSubcategory[[Rule], []]):
    ObjectType = ChosenSubsetObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        ...

    def name(self) -> str:
        ...

    def construction_owner(self) -> Category:
        ...

    def with_cardinality(self, base_set: SetObject, predicate: MembershipRule, cardinality: CardinalObject) -> SetObject:
        ...

    def from_enumeration(self, base_set: SetObject, members: tuple[Datum, ...]) -> SetObject:
        ...

    def characteristic_morphism_of(self, subset: SetObject) -> SetMap:
        ...

    def __call__(self, base_set: SetObject, predicate: MembershipRule) -> SetObject:
        ...

    def image_of(self, set_map: SetMap) -> SetObject:
        ...

class ChosenQuotientObject:

    def quotient_map(self) -> SetMap:
        ...

    def underlying_set(self) -> SetObject:
        ...

class ChosenQuotientsCategory(FullSubcategory[[Rule], []]):
    ObjectType = ChosenQuotientObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        ...

    def name(self) -> str:
        ...

    def __call__(self, base_set: SetObject, class_of: Callable[[Datum], Datum], membership_rule: MembershipRule) -> SetObject:
        ...
