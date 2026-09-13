"""Sage execution for finite binary-relation order laws."""

from __future__ import annotations

from collections.abc import Hashable

from sage.combinat.posets.posets import Poset

__all__ = ["is_partial_order"]


def is_partial_order(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    """Whether ``relation`` is already the complete partial-order relation on ``elements``.

    Sage's ``Poset`` rejects antisymmetry violations and computes the reflexive/transitive
    closure of the supplied relation.  Equality with the original relation therefore
    decides exactly the three finite partial-order laws without reimplementing closure.
    """
    try:
        poset = Poset((elements, tuple(relation)), cover_relations=False)
    except ValueError:
        return False
    closure = frozenset(tuple(pair) for pair in poset.relations_iterator())
    return closure == relation
