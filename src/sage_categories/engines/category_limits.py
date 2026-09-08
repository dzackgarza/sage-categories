"""Finite structural limits of categories through FinSetsForCAP."""

from __future__ import annotations

from collections.abc import Callable

from sage.libs.gap.libgap import libgap

from sage_categories.engines.gap import FINITE_SETS_PACKAGES, load_packages

__all__ = ["compatible_families"]

_loaded = False


def _load() -> None:
    global _loaded
    if not _loaded:
        load_packages(FINITE_SETS_PACKAGES)
        _loaded = True


def compatible_families(
    vertices: tuple[object, ...],
    arrows: tuple[object, ...],
    families: tuple[tuple[object, ...], ...],
    image: Callable[[object, object], object],
) -> tuple[tuple[object, ...], ...]:
    """Return the compatible families selected by the native finite-set limit.

    ``image(u, x)`` is the already-owned action of the category diagram on one
    object or morphism.  GAP owns the compatibility computation; Python only
    translates retained values to and from skeletal finite-set indices.
    """
    _load()
    assert len(vertices) == len(families)
    vertex_positions = {id(vertex): index for index, vertex in enumerate(vertices)}
    value_positions = tuple(
        {id(value): index for index, value in enumerate(family)} for family in families
    )
    native_factors = [libgap.FinSet(len(family)) for family in families]
    decorated = []
    for arrow in arrows:
        source = vertex_positions[id(arrow.domain())]
        target = vertex_positions[id(arrow.codomain())]
        graph = []
        for value in families[source]:
            result = image(arrow, value)
            assert id(result) in value_positions[target], (
                "finite category functor action did not return the retained target value"
            )
            graph.append(value_positions[target][id(result)])
        decorated.append(
            [
                source,
                libgap.MapOfFinSets(native_factors[source], graph, native_factors[target]),
                target,
            ]
        )
    apex = libgap.Limit(libgap.SkeletalFinSets, native_factors, decorated)
    projections = tuple(
        libgap.ProjectionInFactorOfLimitWithGivenLimit(
            libgap.SkeletalFinSets,
            native_factors,
            decorated,
            index,
            apex,
        )
        for index in range(len(vertices))
    )
    graphs = tuple(tuple(int(value) for value in libgap.AsList(projection)) for projection in projections)
    return tuple(
        tuple(families[index][graphs[index][native_index]] for index in range(len(vertices)))
        for native_index in range(int(libgap.Cardinality(apex)))
    )
