"""Sage execution for finite binary-relation order laws."""

from __future__ import annotations

from collections.abc import Hashable

from sage.combinat.posets.posets import FinitePoset, Poset
from sage.graphs.digraph import DiGraph

__all__ = [
    "bottom",
    "covers",
    "height",
    "has_bottom",
    "has_top",
    "is_graded",
    "is_partial_order",
    "is_ranked",
    "is_total_order",
    "linear_extension_leq",
    "rank",
    "rank_of_element",
    "top",
    "width",
]


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
    poset = Poset(graph, cover_relations=False, facade=True)
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


def _required_poset(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> FinitePoset:
    """The exact Sage finite poset represented by an already-owned finite poset."""
    poset = _exact_poset(elements, relation)
    assert poset is not None, "the supplied relation is not an exact finite partial order"
    return poset


def covers(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
    lower: Hashable,
    upper: Hashable,
) -> bool:
    return bool(_required_poset(elements, relation).covers(lower, upper))


def height(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> int:
    if not elements:
        return 0
    return int(_required_poset(elements, relation).height())


def width(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> int:
    if not elements:
        return 0
    return int(_required_poset(elements, relation).width())


def has_bottom(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    return bool(_required_poset(elements, relation).has_bottom())


def has_top(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    return bool(_required_poset(elements, relation).has_top())


def linear_extension_leq(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
    first: Hashable,
    second: Hashable,
) -> bool:
    extension = tuple(_required_poset(elements, relation).linear_extension())
    positions = {value: index for index, value in enumerate(extension)}
    return positions[first] <= positions[second]


def is_ranked(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    return bool(_required_poset(elements, relation).is_ranked())


def is_graded(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> bool:
    return bool(_required_poset(elements, relation).is_graded())


def rank_of_element(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
    element: Hashable,
) -> int:
    return int(_required_poset(elements, relation).rank(element))


def rank(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> int:
    assert elements, "the rank of the empty poset is not defined"
    return int(_required_poset(elements, relation).rank())


def bottom(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> Hashable:
    return _required_poset(elements, relation).bottom()


def top(
    elements: tuple[Hashable, ...],
    relation: frozenset[tuple[Hashable, Hashable]],
) -> Hashable:
    return _required_poset(elements, relation).top()
