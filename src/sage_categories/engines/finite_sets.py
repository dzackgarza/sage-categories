"""FinSetsForCAP execution for finite owned sets and maps.

Owned labels and chosen enumerations remain in ``Sets``.  This module lowers one
finite owned presentation to ``SkeletalFinSets`` through the retained private
bijection and delegates finite-map algorithms to CAP.
"""

from __future__ import annotations

from functools import cache
from typing import Literal

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.engines.gap import FINITE_SETS_PACKAGES, load_packages
from sage_categories.sets._finite_cap import (
    finite_native_morphism,
    finite_native_object,
    retain_finite_native_morphism,
    retain_finite_native_object,
)

__all__ = [
    "cartesian_associator",
    "cartesian_left_unitor",
    "cartesian_right_unitor",
    "equal_morphisms",
    "factor_through_monomorphism",
    "finite_colimit",
    "finite_limit",
    "hom_morphisms",
    "image_factorization",
    "inverse_morphism",
    "is_epimorphism",
    "is_monomorphism",
    "primitive_colimit",
    "primitive_limit",
]


@cache
def _category() -> GapElement:
    load_packages(FINITE_SETS_PACKAGES)
    return libgap.SkeletalFinSets


def _has_native_object(value: object) -> bool:
    try:
        finite_native_object(value)
    except AssertionError:
        return False
    return True


def _has_native_morphism(value: object) -> bool:
    try:
        finite_native_morphism(value)
    except AssertionError:
        return False
    return True


def _index(realization: object, datum: object) -> int:
    indexing = realization.construction.data
    owner = realization.value
    representative = owner.representative(datum)
    for index, candidate in enumerate(indexing):
        if owner.representative(candidate) == representative:
            return index
    raise AssertionError(f"{datum!r} has no private finite index in {owner!r}")


def _native_object(value: object) -> GapElement:
    if _has_native_object(value):
        return finite_native_object(value).native
    indexing = tuple(value._values)
    category = _category()
    native = libgap.FinSet(category, len(indexing))
    retain_finite_native_object(value, native, indexing)
    return native


def _native_morphism(value: MorphismCategory.ObjectType) -> GapElement:
    if _has_native_morphism(value):
        return finite_native_morphism(value).native
    source_record = finite_native_object(value.domain()) if _has_native_object(value.domain()) else None
    target_record = finite_native_object(value.codomain()) if _has_native_object(value.codomain()) else None
    source_native = _native_object(value.domain())
    target_native = _native_object(value.codomain())
    source_record = finite_native_object(value.domain()) if source_record is None else source_record
    target_record = finite_native_object(value.codomain()) if target_record is None else target_record
    graph = [
        _index(target_record, value._action(datum))
        for datum in source_record.construction.data
    ]
    native = libgap.MapOfFinSets(source_native, graph, target_native)
    retain_finite_native_morphism(value, native)
    return native


def _graph(native: GapElement) -> tuple[int, ...]:
    return tuple(int(index) for index in libgap.AsList(native))


def _owned_morphism(
    source: object,
    target: object,
    native: GapElement,
) -> MorphismCategory.ObjectType:
    from sage_categories.sets.finite import Sets

    source_record = finite_native_object(source)
    target_record = finite_native_object(target)
    graph = _graph(native)
    table = {
        datum: target_record.construction.data[graph[index]]
        for index, datum in enumerate(source_record.construction.data)
    }
    owned = Sets.MorphismType(
        domain=source,
        codomain=target,
        data=lambda datum: table[source.representative(datum)],
    )
    retain_finite_native_morphism(owned, native)
    return owned



def cartesian_associator(
    first: object,
    second: object,
    third: object,
    source: object,
    target: object,
    *,
    forward: bool,
) -> MorphismCategory.ObjectType:
    """CAP's selected Cartesian associator on the retained finite-set products."""
    a, b, c = (_native_object(value) for value in (first, second, third))
    native_source, native_target = _native_object(source), _native_object(target)
    match forward:
        case True:
            operation = libgap.CartesianAssociatorLeftToRightWithGivenDirectProducts
        case False:
            operation = libgap.CartesianAssociatorRightToLeftWithGivenDirectProducts
    computed = operation(native_source, a, b, c, native_target)
    return _native_map_on_owned_endpoints(source, target, computed)


def cartesian_left_unitor(
    value: object,
    source: object,
    target: object,
    *,
    forward: bool,
) -> MorphismCategory.ObjectType:
    """CAP's selected left unitor or its inverse on finite sets."""
    native_value = _native_object(value)
    match forward:
        case True:
            computed = libgap.CartesianLeftUnitorWithGivenDirectProduct(native_value, _native_object(source))
        case False:
            computed = libgap.CartesianLeftUnitorInverseWithGivenDirectProduct(native_value, _native_object(target))
    return _native_map_on_owned_endpoints(source, target, computed)


def cartesian_right_unitor(
    value: object,
    source: object,
    target: object,
    *,
    forward: bool,
) -> MorphismCategory.ObjectType:
    """CAP's selected right unitor or its inverse on finite sets."""
    native_value = _native_object(value)
    match forward:
        case True:
            computed = libgap.CartesianRightUnitorWithGivenDirectProduct(native_value, _native_object(source))
        case False:
            computed = libgap.CartesianRightUnitorInverseWithGivenDirectProduct(native_value, _native_object(target))
    return _native_map_on_owned_endpoints(source, target, computed)

def is_monomorphism(value: MorphismCategory.ObjectType) -> bool:
    return bool(libgap.IsMonomorphism(_native_morphism(value)))


def is_epimorphism(value: MorphismCategory.ObjectType) -> bool:
    return bool(libgap.IsEpimorphism(_native_morphism(value)))


def equal_morphisms(
    first: MorphismCategory.ObjectType,
    second: MorphismCategory.ObjectType,
) -> bool:
    return bool(libgap.IsEqualForMorphisms(_native_morphism(first), _native_morphism(second)))


def inverse_morphism(value: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
    native = _native_morphism(value)
    assert bool(libgap.IsIsomorphism(native)), f"{value!r} is not invertible"
    return _owned_morphism(value.codomain(), value.domain(), libgap.InverseForMorphisms(native))


def image_factorization(
    value: MorphismCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    from sage_categories.sets.finite import Sets

    native = _native_morphism(value)
    computed_inclusion = libgap.ImageEmbedding(native)
    target_record = finite_native_object(value.codomain())
    image_indices = _graph(computed_inclusion)
    image_data = tuple(target_record.construction.data[index] for index in image_indices)
    image = Sets(image_data)
    native_image = _native_object(image)
    native_inclusion = libgap.MapOfFinSets(
        native_image, image_indices, _native_object(value.codomain())
    )
    computed_factor = libgap.CoastrictionToImage(native)
    native_factor = libgap.MapOfFinSets(
        _native_object(value.domain()), _graph(computed_factor), native_image
    )
    inclusion = _owned_morphism(image, value.codomain(), native_inclusion)
    factor = _owned_morphism(value.domain(), image, native_factor)
    return factor, inclusion


def factor_through_monomorphism(
    mono: MorphismCategory.ObjectType,
    value: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType | Literal[False]:
    native_value, native_mono = _native_morphism(value), _native_morphism(mono)
    if not bool(libgap.IsLiftable(native_value, native_mono)):
        return False
    return _owned_morphism(value.domain(), mono.domain(), libgap.Lift(native_value, native_mono))


def hom_morphisms(
    source: object,
    target: object,
) -> tuple[MorphismCategory.ObjectType, ...]:
    native_source, native_target = _native_object(source), _native_object(target)
    return tuple(
        _owned_morphism(source, target, native)
        for native in libgap.MorphismsOfExternalHom(native_source, native_target)
    )



def _native_map_on_owned_endpoints(
    source: object,
    target: object,
    computed: GapElement,
) -> MorphismCategory.ObjectType:
    native = libgap.MapOfFinSets(
        _native_object(source), _graph(computed), _native_object(target)
    )
    return _owned_morphism(source, target, native)



def _native_diagram(diagram: object):
    from sage_categories.cat.finite_categories import finite_category
    from sage_categories.cat.predicates import Unknown

    finite = finite_category(diagram.domain())
    assert finite is not Unknown, "native finite-set execution requires exact finite structural data"
    vertices = tuple(finite.objects)
    positions = {id(vertex): index for index, vertex in enumerate(vertices)}
    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    native_factors = [_native_object(factor) for factor in factors]
    decorated = []
    for arrow in finite.morphisms:
        source = positions[id(arrow.domain())]
        target = positions[id(arrow.codomain())]
        decorated.append([source, _native_morphism(diagram.on_morphism(arrow)), target])
    return vertices, positions, factors, native_factors, decorated


def finite_limit(diagram: object) -> object:
    """Selected limit of an arbitrary exact finite diagram, computed by CAP."""
    from sage_categories.cat.cones import cone, cone_apex
    from sage_categories.sets.finite import Sets

    vertices, positions, factors, native_factors, decorated = _native_diagram(diagram)
    category = _category()
    computed_apex = libgap.Limit(category, native_factors, decorated)
    computed_projections = tuple(
        libgap.ProjectionInFactorOfLimitWithGivenLimit(
            category, native_factors, decorated, index, computed_apex
        )
        for index in range(len(vertices))
    )
    records = tuple(finite_native_object(factor) for factor in factors)
    graphs = tuple(_graph(projection) for projection in computed_projections)
    apex_data = tuple(
        tuple(records[index].construction.data[graphs[index][native_index]] for index in range(len(vertices)))
        for native_index in range(int(libgap.Cardinality(computed_apex)))
    )
    apex = Sets(apex_data)
    native_apex = _native_object(apex)
    legs = tuple(
        _native_map_on_owned_endpoints(
            apex,
            factors[index],
            libgap.MapOfFinSets(native_apex, graphs[index], native_factors[index]),
        )
        for index in range(len(vertices))
    )

    def lift(candidate: object) -> MorphismCategory.ObjectType:
        source = cone_apex(candidate)
        tau = [_native_morphism(candidate.component(vertex)) for vertex in vertices]
        computed = libgap.UniversalMorphismIntoLimitWithGivenLimit(
            category, native_factors, decorated, _native_object(source), tau, computed_apex
        )
        return _native_map_on_owned_endpoints(source, apex, computed)

    return Sets.Limits(diagram.domain()).with_universal_data(
        diagram,
        apex,
        cone(diagram, apex, lambda vertex: legs[positions[id(vertex)]]),
        lift,
    )


def finite_colimit(diagram: object) -> object:
    """Selected colimit of an arbitrary exact finite diagram, computed by CAP."""
    from sage_categories.cat.cones import cocone, cocone_apex
    from sage_categories.sets.finite import Sets

    vertices, positions, factors, native_factors, decorated = _native_diagram(diagram)
    category = _category()
    computed_apex = libgap.Colimit(category, native_factors, decorated)
    computed_injections = tuple(
        libgap.InjectionOfCofactorOfColimitWithGivenColimit(
            category, native_factors, decorated, index, computed_apex
        )
        for index in range(len(vertices))
    )
    graphs = tuple(_graph(injection) for injection in computed_injections)
    classes: list[set[object]] = [set() for _ in range(int(libgap.Cardinality(computed_apex)))]
    for factor_index, factor in enumerate(factors):
        record = finite_native_object(factor)
        for source_index, target_index in enumerate(graphs[factor_index]):
            classes[target_index].add((factor_index, record.construction.data[source_index]))
    apex = Sets(tuple(frozenset(part) for part in classes))
    native_apex = _native_object(apex)
    legs = tuple(
        _native_map_on_owned_endpoints(
            factors[index],
            apex,
            libgap.MapOfFinSets(native_factors[index], graphs[index], native_apex),
        )
        for index in range(len(vertices))
    )

    def descent(candidate: object) -> MorphismCategory.ObjectType:
        target = cocone_apex(candidate)
        tau = [_native_morphism(candidate.component(vertex)) for vertex in vertices]
        computed = libgap.UniversalMorphismFromColimitWithGivenColimit(
            category, native_factors, decorated, _native_object(target), tau, computed_apex
        )
        return _native_map_on_owned_endpoints(apex, target, computed)

    return Sets.Colimits(diagram.domain()).with_universal_data(
        diagram,
        apex,
        cocone(diagram, apex, lambda vertex: legs[positions[id(vertex)]]),
        descent,
    )

def _product(diagram: object, vertices: tuple[object, ...]) -> object:
    from sage_categories.cat.cones import cone, cone_apex
    from sage_categories.sets.finite import Sets

    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    native_factors = [_native_object(factor) for factor in factors]
    category = _category()
    computed_apex = libgap.DirectProduct(category, native_factors)
    computed_projections = tuple(
        libgap.ProjectionInFactorOfDirectProductWithGivenDirectProduct(
            category, native_factors, index + 1, computed_apex
        )
        for index in range(len(vertices))
    )
    factor_records = tuple(finite_native_object(factor) for factor in factors)
    projection_graphs = tuple(_graph(projection) for projection in computed_projections)
    apex_data = tuple(
        tuple(
            factor_records[index].construction.data[projection_graphs[index][native_index]]
            for index in range(len(vertices))
        )
        for native_index in range(int(libgap.Cardinality(computed_apex)))
    )
    apex = Sets(apex_data)
    native_apex = _native_object(apex)
    positions = {id(vertex): index for index, vertex in enumerate(vertices)}
    legs = tuple(
        _native_map_on_owned_endpoints(
            apex,
            factors[index],
            libgap.MapOfFinSets(native_apex, projection_graphs[index], native_factors[index]),
        )
        for index in range(len(vertices))
    )

    def lift(candidate: object) -> MorphismCategory.ObjectType:
        source = cone_apex(candidate)
        tau = [_native_morphism(candidate.component(vertex)) for vertex in vertices]
        computed = libgap.UniversalMorphismIntoDirectProductWithGivenDirectProduct(
            category, native_factors, _native_object(source), tau, computed_apex
        )
        return _native_map_on_owned_endpoints(source, apex, computed)

    return Sets.Limits(diagram.domain()).with_universal_data(
        diagram,
        apex,
        cone(diagram, apex, lambda vertex: legs[positions[id(vertex)]]),
        lift,
    )


def _equalizer(diagram: object, vertices: tuple[object, ...]) -> object:
    from sage_categories.cat.cones import cone, cone_apex
    from sage_categories.sets.finite import Sets

    arrows = diagram.domain().generating_morphisms()
    first, second = (diagram.on_morphism(arrow) for arrow in arrows)
    source, target = first.domain(), first.codomain()
    category = _category()
    native_source = _native_object(source)
    native_maps = [_native_morphism(first), _native_morphism(second)]
    computed_apex = libgap.Equalizer(category, native_source, native_maps)
    computed_embedding = libgap.EmbeddingOfEqualizerWithGivenEqualizer(
        category, native_source, native_maps, computed_apex
    )
    source_record = finite_native_object(source)
    embedding_graph = _graph(computed_embedding)
    apex_data = tuple(source_record.construction.data[index] for index in embedding_graph)
    apex = Sets(apex_data)
    native_apex = _native_object(apex)
    embedding_native = libgap.MapOfFinSets(native_apex, embedding_graph, native_source)
    source_leg = _owned_morphism(apex, source, embedding_native)
    target_computed = libgap.PreCompose(category, computed_embedding, native_maps[0])
    target_leg = _native_map_on_owned_endpoints(apex, target, target_computed)
    source_vertex = arrows[0].domain()

    def leg(vertex: object) -> MorphismCategory.ObjectType:
        return source_leg if vertex is source_vertex else target_leg

    def lift(candidate: object) -> MorphismCategory.ObjectType:
        candidate_source = cone_apex(candidate)
        tau = _native_morphism(candidate.component(source_vertex))
        computed = libgap.UniversalMorphismIntoEqualizerWithGivenEqualizer(
            category,
            native_source,
            native_maps,
            _native_object(candidate_source),
            tau,
            computed_apex,
        )
        return _native_map_on_owned_endpoints(candidate_source, apex, computed)

    return Sets.Limits(diagram.domain()).with_universal_data(
        diagram, apex, cone(diagram, apex, leg), lift
    )


def primitive_limit(diagram: object) -> object:
    from sage_categories.cat.finite_categories import finite_category

    shape = diagram.domain()
    vertices = tuple(finite_category(shape).objects)
    if shape.is_discrete():
        return _product(diagram, vertices)
    return _equalizer(diagram, vertices)


def _coproduct(diagram: object, vertices: tuple[object, ...]) -> object:
    from sage_categories.cat.cones import cocone, cocone_apex
    from sage_categories.sets.finite import Sets

    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    native_factors = [_native_object(factor) for factor in factors]
    category = _category()
    computed_apex = libgap.Coproduct(category, native_factors)
    computed_injections = tuple(
        libgap.InjectionOfCofactorOfCoproductWithGivenCoproduct(
            category, native_factors, index + 1, computed_apex
        )
        for index in range(len(vertices))
    )
    injection_graphs = tuple(_graph(injection) for injection in computed_injections)
    apex_labels: list[object | None] = [None] * int(libgap.Cardinality(computed_apex))
    for factor_index, factor in enumerate(factors):
        record = finite_native_object(factor)
        for source_index, target_index in enumerate(injection_graphs[factor_index]):
            apex_labels[target_index] = (factor_index, record.construction.data[source_index])
    assert all(label is not None for label in apex_labels)
    apex = Sets(tuple(apex_labels))
    native_apex = _native_object(apex)
    positions = {id(vertex): index for index, vertex in enumerate(vertices)}
    legs = tuple(
        _native_map_on_owned_endpoints(
            factors[index],
            apex,
            libgap.MapOfFinSets(native_factors[index], injection_graphs[index], native_apex),
        )
        for index in range(len(vertices))
    )

    def descent(candidate: object) -> MorphismCategory.ObjectType:
        target = cocone_apex(candidate)
        tau = [_native_morphism(candidate.component(vertex)) for vertex in vertices]
        computed = libgap.UniversalMorphismFromCoproductWithGivenCoproduct(
            category, native_factors, _native_object(target), tau, computed_apex
        )
        return _native_map_on_owned_endpoints(apex, target, computed)

    return Sets.Colimits(diagram.domain()).with_universal_data(
        diagram,
        apex,
        cocone(diagram, apex, lambda vertex: legs[positions[id(vertex)]]),
        descent,
    )


def _coequalizer(diagram: object, vertices: tuple[object, ...]) -> object:
    from sage_categories.cat.cones import cocone, cocone_apex
    from sage_categories.sets.finite import Sets

    arrows = diagram.domain().generating_morphisms()
    first, second = (diagram.on_morphism(arrow) for arrow in arrows)
    source, target = first.domain(), first.codomain()
    category = _category()
    native_target = _native_object(target)
    native_maps = [_native_morphism(first), _native_morphism(second)]
    computed_apex = libgap.Coequalizer(category, native_target, native_maps)
    computed_projection = libgap.ProjectionOntoCoequalizerWithGivenCoequalizer(
        category, native_target, native_maps, computed_apex
    )
    projection_graph = _graph(computed_projection)
    target_record = finite_native_object(target)
    classes: list[set[object]] = [set() for _ in range(int(libgap.Cardinality(computed_apex)))]
    for source_index, class_index in enumerate(projection_graph):
        classes[class_index].add(target_record.construction.data[source_index])
    apex_data = tuple(frozenset(part) for part in classes)
    apex = Sets(apex_data)
    native_apex = _native_object(apex)
    projection_native = libgap.MapOfFinSets(native_target, projection_graph, native_apex)
    target_leg = _owned_morphism(target, apex, projection_native)
    source_computed = libgap.PreCompose(category, native_maps[0], computed_projection)
    source_leg = _native_map_on_owned_endpoints(source, apex, source_computed)
    source_vertex, target_vertex = arrows[0].domain(), arrows[0].codomain()

    def leg(vertex: object) -> MorphismCategory.ObjectType:
        return source_leg if vertex is source_vertex else target_leg

    def descent(candidate: object) -> MorphismCategory.ObjectType:
        candidate_target = cocone_apex(candidate)
        tau = _native_morphism(candidate.component(target_vertex))
        computed = libgap.UniversalMorphismFromCoequalizerWithGivenCoequalizer(
            category,
            native_target,
            native_maps,
            _native_object(candidate_target),
            tau,
            computed_apex,
        )
        return _native_map_on_owned_endpoints(apex, candidate_target, computed)

    return Sets.Colimits(diagram.domain()).with_universal_data(
        diagram, apex, cocone(diagram, apex, leg), descent
    )


def primitive_colimit(diagram: object) -> object:
    from sage_categories.cat.finite_categories import finite_category

    shape = diagram.domain()
    vertices = tuple(finite_category(shape).objects)
    if shape.is_discrete():
        return _coproduct(diagram, vertices)
    return _coequalizer(diagram, vertices)
