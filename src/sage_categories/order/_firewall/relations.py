"""Finite relation decisions delegated to the order engine."""

from __future__ import annotations

from collections.abc import Hashable

from sage_categories.engines import order_relations as _engine


def partial_order(data: tuple[Hashable, ...], pairs: frozenset[tuple[object, object]]) -> bool:
    return _engine.is_partial_order(data, pairs)


def total_order(data: tuple[Hashable, ...], pairs: frozenset[tuple[object, object]]) -> bool:
    return _engine.is_total_order(data, pairs)


def covers(data, pairs, lower, upper) -> bool:
    return _engine.covers(data, pairs, lower, upper)


def height(data, pairs) -> int:
    return _engine.height(data, pairs)


def width(data, pairs) -> int:
    return _engine.width(data, pairs)


def has_bottom(data, pairs) -> bool:
    return _engine.has_bottom(data, pairs)


def has_top(data, pairs) -> bool:
    return _engine.has_top(data, pairs)


def linear_extension_leq(data, pairs, first, second) -> bool:
    return _engine.linear_extension_leq(data, pairs, first, second)


def is_ranked(data, pairs) -> bool:
    return _engine.is_ranked(data, pairs)


def is_graded(data, pairs) -> bool:
    return _engine.is_graded(data, pairs)


def rank_of_element(data, pairs, element) -> int:
    return _engine.rank_of_element(data, pairs, element)


def rank(data, pairs) -> int:
    return _engine.rank(data, pairs)


def bottom(data, pairs):
    return _engine.bottom(data, pairs)


def top(data, pairs):
    return _engine.top(data, pairs)
