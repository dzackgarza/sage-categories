from collections.abc import Callable
from sage_categories.cat.functors import Functor
from sage_categories.cat.predicates import Decision
from sage_categories.sets.elements import Datum
from sage_categories.sets.category import SetObject
from typing import Any
__all__ = ['Family', 'product_of_sets', 'coproduct_of_sets']

class Family:

    def __init__(self, index_set: SetObject, rule: Callable[[Datum], Datum]) -> None:
        ...

    def index_set(self) -> SetObject:
        ...

    def __call__(self, index_datum: Datum) -> Datum:
        ...

    def __eq__(self, other: Any) -> Decision:
        ...

    def __hash__(self) -> int:
        ...

def product_of_sets(diagram: Functor) -> SetObject:
    ...

def coproduct_of_sets(diagram: Functor) -> SetObject:
    ...
