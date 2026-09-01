from sage.sets.disjoint_set import DisjointSet
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import Decision, UnknownClass
from sage_categories.sets.category import SetMap
from sage_categories.sets.elements import Datum
from sage_categories.sets.category import SetObject
from typing import Any
__all__ = ['limit_of_sets', 'Representative', 'colimit_of_sets']

def limit_of_sets(diagram: Functor) -> SetObject:
    ...

class Representative:

    def __init__(self, quotient: Quotient, tagged: tuple[Datum, Datum]) -> None:
        ...

    def quotient(self) -> Quotient:
        ...

    def tagged(self) -> tuple[Datum, Datum]:
        ...

    def __eq__(self, other: Any) -> Decision:
        ...

    def __hash__(self) -> int:
        ...

class Quotient:

    def __init__(self, diagram: Functor, coproduct: SetObject) -> None:
        ...

    def index_datum(self, member_object: CategoryOfCategories.ElementType) -> Datum:
        ...

    def object_at(self, index_datum: Datum) -> CategoryOfCategories.ElementType:
        ...

    def transition(self, source: Datum, target: Datum) -> SetMap:
        ...

    def partition(self) -> DisjointSet | UnknownClass:
        ...

    def equivalent(self, first: Representative, second: Representative) -> Decision:
        ...

    def hash_of(self, representative: Representative) -> int:
        ...

    def classes(self) -> tuple[Representative, ...]:
        ...

def colimit_of_sets(diagram: Functor) -> SetObject:
    ...
