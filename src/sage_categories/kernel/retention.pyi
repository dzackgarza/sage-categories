from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import partial
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Functor as Functor
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, cached_function as cached_function

def identity_key[Value](*values: Value) -> tuple[tuple[int, Value], ...]:
    ...

def identity_positions[Value](values: tuple[Value, ...]) -> MonoDict:
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
