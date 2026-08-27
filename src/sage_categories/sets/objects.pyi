from sage_categories.cat.category import CategoryDeclaration as CategoryDeclaration
from sage_categories.sets.cardinals import CardinalObjectDeclaration as CardinalObjectDeclaration
from sage_categories.sets.category import Sets_Countable_ObjectType as Sets_Countable_ObjectType
from sage_categories.sets.elements import SetElementDeclaration as SetElementDeclaration
import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from sage.structure.coerce_dict import MonoDict
from sage_categories.cat.category import Category as Category
from sage_categories.kernel.decisions import Decision as Decision, Unknown as Unknown, UnknownClass as UnknownClass
from sage_categories.kernel.predicates import AppliedPredicate as AppliedPredicate, Predicate as Predicate, ask as ask
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, ObjectOfCategory as ObjectOfCategory, Role as Role, role_of as role_of
from sage_categories.sets.cardinals import CardinalObject as CardinalObject
from sage_categories.sets.category import SetElement as SetElement, SetObject as SetObject
from sage_categories.sets.elements import Datum as Datum, SetPointData as SetPointData
from typing import Any

logger: logging.Logger
type MembershipRule = Callable[[Datum], Decision]
element_of: Predicate

@dataclass(eq=False, slots=True)
class SetObjectData:
    membership_rule: MembershipRule
    cardinality: CardinalObject | UnknownClass
    points: dict[Datum, SetElement] = field(default_factory=dict)
    rule_points: MonoDict = field(default_factory=MonoDict)
    canonical: SetObject = field(init=False)
    def bind(self, canonical: SetObject) -> None: ...

class SetObjectDeclaration(ObjectOfCategory):
    def __init__(self, data: SetObjectData) -> None: ...
    def membership_proposition(self, candidate: CategoryPoint) -> AppliedPredicate: ...
    def __contains__(self, candidate: Any) -> bool: ...
    def point(self, datum: Datum) -> SetElement: ...
    def rule_point(self, datum: Datum) -> SetElement: ...
    def cardinality(self) -> CardinalObject | UnknownClass: ...
    def subset_from(self, predicate: MembershipRule) -> SetObject: ...
    def is_finite(self) -> AppliedPredicate: ...
    def is_infinite(self) -> AppliedPredicate: ...
    def is_countable(self) -> AppliedPredicate: ...
    def is_uncountable(self) -> AppliedPredicate: ...

class FiniteSetRole(Sets_Countable_ObjectType, SetObjectDeclaration):
    def __iter__(self) -> Iterator[SetElement]: ...
