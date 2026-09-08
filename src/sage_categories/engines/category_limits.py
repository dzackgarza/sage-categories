"""Finite structural limits of categories through FinSetsForCAP."""

from __future__ import annotations

from collections.abc import Callable

from sage.libs.gap.libgap import libgap

from sage_categories.engines.gap import FINITE_SETS_PACKAGES, load_packages

__all__ = ["compatible_families", "matching_triples"]

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
    locate: Callable[[tuple[object, ...], object], int],
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
            match id(result) in value_positions[target]:
                case True:
                    graph.append(value_positions[target][id(result)])
                case False:
                    graph.append(locate(families[target], result))
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


def matching_triples(
    source_values: tuple[object, ...],
    target_values: tuple[object, ...],
    morphisms: tuple[object, ...],
    reindex: Callable[[object], object],
    domain: Callable[[object], object],
    codomain: Callable[[object], object],
    locate: Callable[[tuple[object, ...], object], int],
) -> tuple[tuple[object, object, object], ...]:
    """Native finite join for triples ``(x, y, phi)`` with ``phi: x -> P(f)(y)``.

    CAP owns the product and equalizer computation. Python supplies only the
    already-owned finite values and converts their retained identities to skeletal
    indices.
    """
    _load()
    category = libgap.SkeletalFinSets
    native_source = libgap.FinSet(len(source_values))
    native_target = libgap.FinSet(len(target_values))
    native_morphisms = libgap.FinSet(len(morphisms))
    factors = [native_source, native_target, native_morphisms]
    product = libgap.DirectProduct(category, factors)
    projections = tuple(
        libgap.ProjectionInFactorOfDirectProductWithGivenDirectProduct(
            category, factors, index + 1, product
        )
        for index in range(3)
    )

    def graph(values: tuple[object, ...], target: tuple[object, ...], action: Callable[[object], object]) -> list[int]:
        return [locate(target, action(value)) for value in values]

    domain_map = libgap.MapOfFinSets(
        native_morphisms, graph(morphisms, source_values, domain), native_source
    )
    codomain_map = libgap.MapOfFinSets(
        native_morphisms, graph(morphisms, source_values, codomain), native_source
    )
    reindex_map = libgap.MapOfFinSets(
        native_target, graph(target_values, source_values, reindex), native_source
    )
    left_components = [
        projections[0],
        libgap.PreCompose(category, projections[2], codomain_map),
    ]
    right_components = [
        libgap.PreCompose(category, projections[2], domain_map),
        libgap.PreCompose(category, projections[1], reindex_map),
    ]
    pair_target_factors = [native_source, native_source]
    pair_target = libgap.DirectProduct(category, pair_target_factors)
    left = libgap.UniversalMorphismIntoDirectProductWithGivenDirectProduct(
        category, pair_target_factors, product, left_components, pair_target
    )
    right = libgap.UniversalMorphismIntoDirectProductWithGivenDirectProduct(
        category, pair_target_factors, product, right_components, pair_target
    )
    equalizer = libgap.Equalizer(category, product, [left, right])
    embedding = libgap.EmbeddingOfEqualizerWithGivenEqualizer(
        category, product, [left, right], equalizer
    )
    selected = tuple(int(value) for value in libgap.AsList(embedding))
    projection_graphs = tuple(
        tuple(int(value) for value in libgap.AsList(projection)) for projection in projections
    )
    return tuple(
        (
            source_values[projection_graphs[0][index]],
            target_values[projection_graphs[1][index]],
            morphisms[projection_graphs[2][index]],
        )
        for index in selected
    )
