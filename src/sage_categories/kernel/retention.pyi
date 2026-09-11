from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import partial
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
__all__ = ['identity_key', 'complete_constructions', 'category_construction_functors', 'deferred_category', 'retained_involution']

def identity_key[Value](*values: Value) -> tuple[tuple[int, Value], ...]:
    ...

@contextmanager
def complete_constructions() -> Iterator[None]:
    ...

def category_construction_functors(category: Category) -> tuple[Functor, ...]:
    ...

def deferred_category[Value: Category, Parameter](constructor: type[Value] | partial[Value], parameter: Parameter) -> Value:
    ...

def retained_involution[Value](construct: Callable[[Value], Value]) -> Callable[[Value], Value]:
    ...
