"""Identity keys and construction ordering over Sage's retained functions.

Sage ``cached_function`` owns argument normalization and storage. Reciprocal
identifications add a second key for a result before dependent declarations run.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from graphlib import TopologicalSorter
from typing import TYPE_CHECKING

from sage_categories.kernel.sage_runtime import cached_function

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = ["category_construction_functors", "deferred_category", "identity_key", "retained_involution"]


def identity_key[Value](*values: Value) -> tuple[tuple[int, Value], ...]:
    """Keep each argument alive and compare its identity before its equality."""
    return tuple((id(value), value) for value in values)


_deferred_category: ContextVar[Category | None] = ContextVar("deferred category", default=None)
_completions: ContextVar[deque[Category] | None] = ContextVar("category completions", default=None)


@contextmanager
def _complete_constructions() -> Iterator[None]:
    if _completions.get() is not None:
        yield
        return
    pending: deque[Category] = deque()
    token = _completions.set(pending)
    try:
        yield
        declarations: dict[int, tuple[Category, tuple[Functor, ...]]] = {}
        while pending:
            category = pending.popleft()
            declarations[id(category)] = (category, category._complete_declarations())
        dependencies = {
            key: tuple(
                id(functor.codomain())
                for functor in functors
                if id(functor.codomain()) in declarations and functor.codomain() is not category
            )
            for key, (category, functors) in declarations.items()
        }
        for key in TopologicalSorter(dependencies).static_order():
            category, functors = declarations[key]
            category._recompile_category(functors)
    finally:
        _completions.reset(token)


def category_construction_functors(category: Category) -> tuple[Functor, ...]:
    """Read declarations after a staged category has its retained identity."""
    if _deferred_category.get() is category:
        return ()
    return category._select_functors()


def deferred_category[Value: Category, Parameter](constructor: type[Value], parameter: Parameter) -> Value:
    """Initialize one category now and complete its declarations after retention."""
    pending = _completions.get()
    assert pending is not None, "staged category construction requires a retained construction"
    category = constructor.__new__(constructor)
    token = _deferred_category.set(category)
    try:
        constructor.__init__(category, parameter)
    finally:
        _deferred_category.reset(token)
    pending.append(category)
    return category


def retained_involution[Value](construct: Callable[[Value], Value]) -> Callable[[Value], Value]:
    """Retain both directions of a declared identity correspondence."""
    retained = cached_function(construct, key=identity_key)

    @wraps(construct)
    def apply(value: Value) -> Value:
        if retained.is_in_cache(value):
            return retained(value)
        with _complete_constructions():
            result = retained(value)
            if retained.is_in_cache(result):
                assert retained(result) is value, "the retained correspondence must be involutive"
            else:
                retained.set_cache(value, result)
        return result

    return apply
