from sage_categories.cat.predicates import Decision
from sage_categories.sets.category import SetMap
from sage_categories.sets.category import SetElement
from sage_categories.sets.category import SetObject
from typing import Any
__all__ = ['Function', 'function_set', 'name_of', 'evaluation_morphism', 'transpose']

class Function:

    def __init__(self, set_map: SetMap) -> None:
        ...

    def map(self) -> SetMap:
        ...

    def __eq__(self, other: Any) -> Decision:
        ...

    def __hash__(self) -> int:
        ...

def function_set(exponent: SetObject, base: SetObject) -> SetObject:
    ...

def name_of(set_map: SetMap) -> SetElement:
    ...

def evaluation_morphism(exponent: SetObject, base: SetObject) -> SetMap:
    ...

def transpose(set_map: SetMap) -> SetMap:
    ...
