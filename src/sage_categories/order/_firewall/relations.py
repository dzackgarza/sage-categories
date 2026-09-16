"""Finite relation decisions delegated to the order engine."""

from __future__ import annotations

from collections.abc import Hashable, Iterable

from sage_categories.engines.order_relations import is_partial_order, is_total_order


def partial_order(data: tuple[Hashable, ...], pairs: frozenset[tuple[object, object]]) -> bool:
    return is_partial_order(data, pairs)


def total_order(data: tuple[Hashable, ...], pairs: frozenset[tuple[object, object]]) -> bool:
    return is_total_order(data, pairs)
