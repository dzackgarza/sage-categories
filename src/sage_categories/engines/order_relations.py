"""Sage execution for finite binary-relation order laws."""

from __future__ import annotations

from collections.abc import Hashable

from sage.combinat.posets.posets import FinitePoset, Poset
from sage.graphs.digraph import DiGraph

__all__ = ["is_partial_order", "is_total_order"]


def _exact_poset(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> FinitePoset | None:
    """Return Sage's finite poset exactly when ``relation`` already is its full order."""
    graph = DiGraph()
    graph.add_vertices(elements)
    graph.add_edges(relation, loops=False)
    if not graph.is_directed_acyclic():
        return None
    poset = Poset(graph, cover_relations=False)
    closure = frozenset(tuple(pair) for pair in poset.relations_iterator())
    return poset if closure == relation else None


def is_partial_order(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    """Whether ``relation`` is already the complete partial-order relation on ``elements``.

    Sage's directed-graph decision rejects non-antisymmetric cycles before ``Poset``
    computes the reflexive/transitive closure.  Equality with the original relation then
    decides exactly the three finite partial-order laws without reimplementing closure.
    """
    return _exact_poset(elements, relation) is not None


def is_total_order(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    """Whether ``relation`` is exactly a finite total order on ``elements``."""
    poset = _exact_poset(elements, relation)
    return poset is not None and poset.is_chain()
