import sage_categories
from _typeshed import Incomplete
from collections.abc import Hashable
from dataclasses import dataclass
from sage_categories.cat.category import Category
from sage_categories.cat.predicates import AppliedPredicate, Predicate, UnknownClass
from sage_categories.sets.cardinals import CardinalObject
__all__ = ['bind_cardinals', 'initial', 'at_most', 'less_than', 'OrdinalsCategory', 'OrdinalObject', 'Ordinals', 'ordinal', 'omega', 'omega0', 'OrdinalOrder']

def bind_cardinals() -> None:
    ...
type Key = tuple[Hashable, ...]

@dataclass(frozen=True, eq=False, slots=True)
class OrdinalObjectData:
    key: Key
    terms: tuple[OrdinalObject, ...]

class OrdinalObjectDeclaration(sage_categories.kernel.roles.ObjectOfCategory):

    def __init__(self, data: OrdinalObjectData) -> None:
        ...

    def is_initial(self) -> AppliedPredicate:
        ...

    def initial_index(self) -> OrdinalObject:
        ...

    def cardinality(self) -> CardinalObject:
        ...

    def cofinality(self) -> CardinalObject | UnknownClass:
        ...

    def __add__(self, other: OrdinalObject | int) -> OrdinalObject:
        ...

    def __radd__(self, other: int) -> OrdinalObject:
        ...

    def __mul__(self, other: OrdinalObject | int) -> OrdinalObject:
        ...

    def __rmul__(self, other: int) -> OrdinalObject:
        ...

    def ordinal_sum(self, other: OrdinalObject | int) -> OrdinalObject:
        ...

    def ordinal_product(self, other: OrdinalObject | int) -> OrdinalObject:
        ...

    def ordinal_power(self, exponent: OrdinalObject | int) -> OrdinalObject:
        ...

    def __le__(self, other: OrdinalObject | int) -> AppliedPredicate:
        ...

    def __lt__(self, other: OrdinalObject | int) -> AppliedPredicate:
        ...

    def __ge__(self, other: OrdinalObject | int) -> AppliedPredicate:
        ...

    def __gt__(self, other: OrdinalObject | int) -> AppliedPredicate:
        ...

    def __hash__(self) -> int:
        ...
initial: Predicate
at_most: Predicate
less_than: Predicate

class OrdinalsCategory(Category[[], []]):
    ObjectType = OrdinalObjectDeclaration

    class ElementType(sage_categories.kernel.roles.ElementOfObject):
        ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory):
        ...

    def __init__(self) -> None:
        ...

    def __call__(self, value: OrdinalObject | int) -> OrdinalObject:
        ...

    def omega(self, index: OrdinalObject | int) -> OrdinalObject:
        ...

    def zero(self) -> OrdinalObject:
        ...

    def one(self) -> OrdinalObject:
        ...

    def natural_sum(self, *summands: OrdinalObject) -> OrdinalObject:
        ...

    def natural_product(self, *factors: OrdinalObject) -> OrdinalObject:
        ...

    def ordinal_sum(self, left: OrdinalObject, right: OrdinalObject) -> OrdinalObject:
        ...

    def ordinal_product(self, left: OrdinalObject, right: OrdinalObject) -> OrdinalObject:
        ...

    def ordinal_power(self, base: OrdinalObject, exponent: OrdinalObject) -> OrdinalObject:
        ...
OrdinalObject: Incomplete

def Ordinals() -> OrdinalsCategory:
    ...

def ordinal(value: OrdinalObject | int) -> OrdinalObject:
    ...

def omega(index: OrdinalObject | int) -> OrdinalObject:
    ...
omega0: OrdinalObject

def OrdinalOrder() -> Category:
    ...
