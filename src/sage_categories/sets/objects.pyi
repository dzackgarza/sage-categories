from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from sage.structure.coerce_dict import MonoDict
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.predicates import AppliedPredicate, Decision, Predicate, Proposition, UnknownClass
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.category import SetElement, SetMap, SetObject
from sage_categories.sets.elements import Datum
from typing import Any
__all__ = ['MembershipRule', 'element_of', 'sets_equal', 'SetObjectData']
type MembershipRule = Callable[[Datum], Decision]
element_of: Predicate

def sets_equal(first: CategoryOfCategories.ElementType, candidate: Any, assumptions: Proposition) -> Decision:
    ...

@dataclass(eq=False, slots=True)
class SetObjectData:
    membership_rule: MembershipRule
    cardinality: CardinalObject | UnknownClass
    points: dict[Datum, SetElement] = field(default_factory=dict)
    rule_points: MonoDict = field(default_factory=MonoDict)

class SetObjectDeclaration:

    def __init__(self, data: SetObjectData) -> None:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> AppliedPredicate:
        ...

    def __contains__(self, candidate: Any) -> bool:
        ...

    def point(self, datum: Datum) -> SetElement:
        ...

    def rule_point(self, datum: Datum) -> SetElement:
        ...

    def cardinality(self) -> CardinalObject | UnknownClass:
        ...

    def subset_from(self, predicate: MembershipRule) -> SetObject:
        ...

    def is_finite(self) -> AppliedPredicate:
        ...

    def is_infinite(self) -> AppliedPredicate:
        ...

    def is_countable(self) -> AppliedPredicate:
        ...

    def is_uncountable(self) -> AppliedPredicate:
        ...

    def evaluation_isomorphism(self) -> SetMap:
        ...

class FiniteSetObject:

    def __iter__(self) -> Iterator[SetElement]:
        ...
