"""Exact finite set engines: products and equivalence closures."""

from collections.abc import Hashable, Iterable
from itertools import product

from networkx import Graph, connected_components


def cartesian(
    factors: Iterable[tuple[Hashable, ...]],
) -> tuple[tuple[Hashable, ...], ...]:
    return tuple(product(*factors))


def quotient(
    values: tuple[Hashable, ...], pairs: Iterable[tuple[Hashable, Hashable]]
) -> dict[Hashable, frozenset[Hashable]]:
    graph = Graph()
    graph.add_nodes_from(values)
    graph.add_edges_from(pairs)
    return {
        value: frozenset(component)
        for component in connected_components(graph)
        for value in component
    }
