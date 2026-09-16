"""Private lowering and reconstruction at the finite-poset/Sage boundary.

Theory passes owned relation objects and owned set morphisms.  This module lowers only
finite data, delegates order-law decisions to the Sage engine, and reconstructs target
comparisons through the original owned poset.  No Sage element or backend container
crosses back into the theory layer.
"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

from sympy import ask as sympy_ask

from sage_categories.cat.predicates import Proposition, Unknown
from sage_categories.order._firewall import relations as _relations
from sage_categories.sets.finite import Sets


def _finite_relation(
    relation_object: Any,
) -> tuple[tuple[Hashable, ...], frozenset[tuple[Hashable, Hashable]]] | None:
    """Lower an exact finite owned relation to data understood by the Sage adapter."""
    carrier_points = Sets.finite_points(relation_object.carrier())
    relation_points = Sets.finite_points(relation_object.relation().arrow().domain())
    if carrier_points is Unknown or relation_points is Unknown:
        return None
    return (
        tuple(point.datum() for point in carrier_points),
        frozenset(point.datum() for point in relation_points),
    )


def partial_order(relation_object: Any) -> bool | None:
    """Decide the partial-order laws exactly when the owned relation is finite and explicit."""
    lowered = _finite_relation(relation_object)
    if lowered is None:
        return None
    data, pairs = lowered
    return _relations.partial_order(data, pairs)


def total_order(poset_object: Any) -> bool | None:
    """Decide totality exactly when the owned order is finite and explicit."""
    lowered = _finite_relation(poset_object)
    if lowered is None:
        return None
    data, pairs = lowered
    return _relations.total_order(data, pairs)


def order_preserving(
    source: Any,
    target: Any,
    underlying: Any,
    assumptions: Proposition,
) -> bool | None:
    """Decide monotonicity by the exact finite source relation.

    The candidate is already an owned set morphism.  Images are immediately lifted back
    to canonical elements of ``target`` before its order proposition is asked, so neither
    raw callables nor backend/Sage elements become mathematical maps or points.
    """
    lowered = _finite_relation(source)
    if lowered is None:
        return None
    _, source_pairs = lowered
    source_carrier = source.carrier()
    undecided = False
    for first_datum, second_datum in source_pairs:
        first_image = underlying(source_carrier.point(first_datum))
        second_image = underlying(source_carrier.point(second_datum))
        first = target.point(first_image.datum())
        second = target.point(second_image.datum())
        decision = sympy_ask(target.related(first, second), assumptions)
        if decision is False:
            return False
        undecided = undecided or decision is None
    return None if undecided else True
