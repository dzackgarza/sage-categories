"""FinSetsForCAP execution for finite owned sets and maps.

Owned labels and chosen enumerations remain in ``Sets``.  This module lowers one
finite owned presentation to ``SkeletalFinSets`` through the retained private
bijection and delegates finite-map algorithms to CAP.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from types import ModuleType
from typing import TYPE_CHECKING, Literal

from sage.libs.gap.element import GapElement
from sage.libs.gap.libgap import libgap

from sage_categories.cat.declarations import Sets
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.predicates import Unknown, UnknownClass
from sage_categories.engines.gap import FINITE_SETS_PACKAGES, load_packages
from sage_categories.kernel.retention import identity_positions
from sage_categories.kernel.sage_runtime import MonoDict
from sage_categories.sets._finite_cap import (
    finite_native_morphism,
    finite_native_object,
    has_finite_native_morphism,
    has_finite_native_object,
    retain_finite_native_morphism,
    retain_finite_native_object,
)

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.cones import ConeCategory
    from sage_categories.cat.finite_categories import FiniteCategoryData
    from sage_categories.cat.functors import Functor

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


def _owned_map_value(arrow: MorphismCategory.ObjectType, datum: object) -> object:
    """Evaluate one owned set map through its public point action and return the target datum."""
    return arrow(arrow.domain().point(datum)).datum()


@cache
def _category() -> GapElement:
    load_packages(FINITE_SETS_PACKAGES)
    return libgap.SkeletalFinSets


def _finite_category_data(
    category: CategoryOfCategories.ElementType,
) -> FiniteCategoryData | UnknownClass:
    """Evaluate a finite category lazily so this engine does not enter the category evaluator during import."""
    from sage_categories.cat.finite_categories import finite_category

    return finite_category(category)


def _cones() -> ModuleType:
    """Load cone/cocone execution at the one cycle-safe finite-set engine boundary."""
    from sage_categories.cat import cones

    return cones


def _index(realization: object, datum: object) -> int:
    indexing = realization.construction.data
    owner = realization.value
    representative = owner.representative(datum)
    for index, candidate in enumerate(indexing):
        if owner.representative(candidate) == representative:
            return index
    raise AssertionError(f"{datum!r} has no private finite index in {owner!r}")


def _native_object(value: object) -> GapElement:
    if has_finite_native_object(value):
        return finite_native_object(value).native
    presentation = value.set_presentation()
    assert isinstance(presentation, tuple), f"{value!r} has no chosen finite presentation"
    indexing = presentation
    category = _category()
    native = libgap.FinSet(category, len(indexing))
    retain_finite_native_object(value, native, indexing)
    return native


def _native_object_if_finite(value: object) -> GapElement | None:
    """Return the native finite realization when ``value`` is exactly finite, else ``None``.

    Universal maps out of or into a CAP-selected finite construction still range over
    arbitrary owned sets.  Their source/target is lowered only when the owned finite-set
    evaluator applies on that endpoint.
    """
    from sage_categories.sets.finite import _finite_data

    if _finite_data(value) is Unknown:
        return None
    return _native_object(value)


def _native_morphism(value: MorphismCategory.ObjectType) -> GapElement:
    if has_finite_native_morphism(value):
        return finite_native_morphism(value).native
    source_native = _native_object(value.domain())
    target_native = _native_object(value.codomain())
    source_record = finite_native_object(value.domain())
    target_record = finite_native_object(value.codomain())
    graph = [_index(target_record, _owned_map_value(value, datum)) for datum in source_record.construction.data]
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
    source_record = finite_native_object(source)
    target_record = finite_native_object(target)
    graph = _graph(native)
    table = {datum: target_record.construction.data[graph[index]] for index, datum in enumerate(source_record.construction.data)}
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
    native = _native_morphism(value)
    computed_inclusion = libgap.ImageEmbedding(native)
    target_record = finite_native_object(value.codomain())
    image_indices = _graph(computed_inclusion)
    image_data = tuple(target_record.construction.data[index] for index in image_indices)
    image = Sets(image_data)
    native_image = _native_object(image)
    native_inclusion = libgap.MapOfFinSets(native_image, image_indices, _native_object(value.codomain()))
    computed_factor = libgap.CoastrictionToImage(native)
    native_factor = libgap.MapOfFinSets(_native_object(value.domain()), _graph(computed_factor), native_image)
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
    return tuple(_owned_morphism(source, target, native) for native in libgap.MorphismsOfExternalHom(native_source, native_target))


def _native_map_on_owned_endpoints(
    source: object,
    target: object,
    computed: GapElement,
) -> MorphismCategory.ObjectType:
    native = libgap.MapOfFinSets(_native_object(source), _graph(computed), _native_object(target))
    return _owned_morphism(source, target, native)


def _parallel_pair_leg(
    source_vertex: object,
    source_leg: MorphismCategory.ObjectType,
    target_leg: MorphismCategory.ObjectType,
) -> Callable[[object], MorphismCategory.ObjectType]:
    """Return the two-leg selector shared by equalizer and coequalizer presentations."""

    def leg(vertex: object) -> MorphismCategory.ObjectType:
        return source_leg if vertex is source_vertex else target_leg

    return leg


def _parallel_pair_data(
    diagram: Functor,
) -> tuple[
    tuple[MorphismCategory.ObjectType, ...],
    object,
    object,
    GapElement,
    list[GapElement],
]:
    """Lower one walking parallel pair to its shared owned/native endpoint data."""
    arrows = tuple(diagram.domain().generating_morphisms())
    maps = tuple(diagram.on_morphism(arrow) for arrow in arrows)
    assert len(maps) == 2
    source, target = maps[0].domain(), maps[0].codomain()
    assert all(arrow.domain() is source and arrow.codomain() is target for arrow in maps)
    return arrows, source, target, _category(), [_native_morphism(arrow) for arrow in maps]


def _finite_discrete_factors(
    diagram: Functor,
    vertices: tuple[object, ...],
) -> tuple[tuple[object, ...], list[GapElement], GapElement, MonoDict]:
    """Lower the factors of one finite discrete diagram once for product/coproduct execution."""
    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    return factors, [_native_object(factor) for factor in factors], _category(), identity_positions(vertices)


def _native_components(
    candidate: ConeCategory.ObjectType,
    vertices: tuple[object, ...],
) -> list[GapElement]:
    """Lower a cone/cocone component family to the retained native finite maps."""
    return [_native_morphism(candidate.component(vertex)) for vertex in vertices]


def _native_diagram(diagram: Functor):
    finite = _finite_category_data(diagram.domain())
    assert finite is not Unknown, "native finite-set execution requires exact finite structural data"
    vertices = tuple(finite.objects)
    positions = identity_positions(vertices)
    factors = tuple(diagram.on_object(vertex) for vertex in vertices)
    native_factors = [_native_object(factor) for factor in factors]
    decorated = []
    for arrow in finite.morphisms:
        source = positions[arrow.domain()]
        target = positions[arrow.codomain()]
        decorated.append([source, _native_morphism(diagram.on_morphism(arrow)), target])
    return vertices, positions, factors, native_factors, decorated


def finite_limit(diagram: Functor) -> object:
    """Selected limit of an arbitrary exact finite diagram, computed by CAP."""
    cones = _cones()

    vertices, positions, factors, native_factors, decorated = _native_diagram(diagram)
    category = _category()
    computed_apex = libgap.Limit(category, native_factors, decorated)
    computed_projections = tuple(libgap.ProjectionInFactorOfLimitWithGivenLimit(category, native_factors, decorated, index, computed_apex) for index in range(len(vertices)))
    records = tuple(finite_native_object(factor) for factor in factors)
    graphs = tuple(_graph(projection) for projection in computed_projections)
    apex_data = tuple(
        tuple(records[index].construction.data[graphs[index][native_index]] for index in range(len(vertices))) for native_index in range(int(libgap.Cardinality(computed_apex)))
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

    def lift(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        source = cones.cone_apex(candidate)
        native_source = _native_object_if_finite(source)
        if native_source is None:
            components = tuple(candidate.component(vertex) for vertex in vertices)
            return diagram.codomain().construct_morphism(
                source,
                apex,
                lambda value: tuple(_owned_map_value(component, value) for component in components),
            )
        tau = _native_components(candidate, vertices)
        computed = libgap.UniversalMorphismIntoLimitWithGivenLimit(category, native_factors, decorated, native_source, tau, computed_apex)
        return _native_map_on_owned_endpoints(source, apex, computed)

    return (
        diagram.codomain()
        .Limits(diagram.domain())
        .with_universal_data(
            diagram,
            apex,
            cones.cone(diagram, apex, lambda vertex: legs[positions[vertex]]),
            lift,
        )
    )


def finite_colimit(diagram: Functor) -> object:
    """Selected colimit of an arbitrary exact finite diagram, computed by CAP."""
    cones = _cones()

    vertices, positions, factors, native_factors, decorated = _native_diagram(diagram)
    category = _category()
    computed_apex = libgap.Colimit(category, native_factors, decorated)
    computed_injections = tuple(
        libgap.InjectionOfCofactorOfColimitWithGivenColimit(category, native_factors, decorated, index, computed_apex) for index in range(len(vertices))
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

    def descent(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        target = cones.cocone_apex(candidate)
        native_target = _native_object_if_finite(target)
        if native_target is None:
            components = tuple(candidate.component(vertex) for vertex in vertices)

            def evaluate(part: frozenset[tuple[int, object]]) -> object:
                factor_index, datum = next(iter(part))
                return _owned_map_value(components[factor_index], datum)

            return diagram.codomain().construct_morphism(apex, target, evaluate)
        tau = _native_components(candidate, vertices)
        computed = libgap.UniversalMorphismFromColimitWithGivenColimit(category, native_factors, decorated, native_target, tau, computed_apex)
        return _native_map_on_owned_endpoints(apex, target, computed)

    return (
        diagram.codomain()
        .Colimits(diagram.domain())
        .with_universal_data(
            diagram,
            apex,
            cones.cocone(diagram, apex, lambda vertex: legs[positions[vertex]]),
            descent,
        )
    )


def _product(diagram: Functor, vertices: tuple[object, ...]) -> object:
    cones = _cones()

    factors, native_factors, category, positions = _finite_discrete_factors(diagram, vertices)
    computed_apex = libgap.DirectProduct(category, native_factors)
    computed_projections = tuple(
        libgap.ProjectionInFactorOfDirectProductWithGivenDirectProduct(category, native_factors, index + 1, computed_apex) for index in range(len(vertices))
    )
    factor_records = tuple(finite_native_object(factor) for factor in factors)
    projection_graphs = tuple(_graph(projection) for projection in computed_projections)
    apex_data = tuple(
        tuple(factor_records[index].construction.data[projection_graphs[index][native_index]] for index in range(len(vertices)))
        for native_index in range(int(libgap.Cardinality(computed_apex)))
    )
    apex = Sets(apex_data)
    native_apex = _native_object(apex)
    legs = tuple(
        _native_map_on_owned_endpoints(
            apex,
            factors[index],
            libgap.MapOfFinSets(native_apex, projection_graphs[index], native_factors[index]),
        )
        for index in range(len(vertices))
    )

    def lift(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        source = cones.cone_apex(candidate)
        native_source = _native_object_if_finite(source)
        if native_source is None:
            components = tuple(candidate.component(vertex) for vertex in vertices)
            return diagram.codomain().construct_morphism(
                source,
                apex,
                lambda value: tuple(_owned_map_value(component, value) for component in components),
            )
        tau = _native_components(candidate, vertices)
        computed = libgap.UniversalMorphismIntoDirectProductWithGivenDirectProduct(category, native_factors, native_source, tau, computed_apex)
        return _native_map_on_owned_endpoints(source, apex, computed)

    return (
        diagram.codomain()
        .Limits(diagram.domain())
        .with_universal_data(
            diagram,
            apex,
            cones.cone(diagram, apex, lambda vertex: legs[positions[vertex]]),
            lift,
        )
    )


def _equalizer(diagram: Functor, vertices: tuple[object, ...]) -> object:
    cones = _cones()

    arrows, source, target, category, native_maps = _parallel_pair_data(diagram)
    native_source = _native_object(source)
    computed_apex = libgap.Equalizer(category, native_source, native_maps)
    computed_embedding = libgap.EmbeddingOfEqualizerWithGivenEqualizer(category, native_source, native_maps, computed_apex)
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

    leg = _parallel_pair_leg(source_vertex, source_leg, target_leg)

    def lift(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        candidate_source = cones.cone_apex(candidate)
        candidate_native = _native_object_if_finite(candidate_source)
        component = candidate.component(source_vertex)
        if candidate_native is None:
            return diagram.codomain().construct_morphism(candidate_source, apex, lambda datum: _owned_map_value(component, datum))
        tau = _native_morphism(component)
        computed = libgap.UniversalMorphismIntoEqualizerWithGivenEqualizer(
            category,
            native_source,
            native_maps,
            candidate_native,
            tau,
            computed_apex,
        )
        return _native_map_on_owned_endpoints(candidate_source, apex, computed)

    return diagram.codomain().Limits(diagram.domain()).with_universal_data(diagram, apex, cones.cone(diagram, apex, leg), lift)


def primitive_limit(diagram: Functor) -> object:
    shape = diagram.domain()
    vertices = tuple(_finite_category_data(shape).objects)
    if shape.is_discrete():
        return _product(diagram, vertices)
    return _equalizer(diagram, vertices)


def _coproduct(diagram: Functor, vertices: tuple[object, ...]) -> object:
    cones = _cones()

    factors, native_factors, category, positions = _finite_discrete_factors(diagram, vertices)
    computed_apex = libgap.Coproduct(category, native_factors)
    computed_injections = tuple(libgap.InjectionOfCofactorOfCoproductWithGivenCoproduct(category, native_factors, index + 1, computed_apex) for index in range(len(vertices)))
    injection_graphs = tuple(_graph(injection) for injection in computed_injections)
    apex_labels: list[object | None] = [None] * int(libgap.Cardinality(computed_apex))
    for factor_index, factor in enumerate(factors):
        record = finite_native_object(factor)
        for source_index, target_index in enumerate(injection_graphs[factor_index]):
            apex_labels[target_index] = (
                factor_index,
                record.construction.data[source_index],
            )
    assert all(label is not None for label in apex_labels)
    apex = Sets(tuple(apex_labels))
    native_apex = _native_object(apex)
    legs = tuple(
        _native_map_on_owned_endpoints(
            factors[index],
            apex,
            libgap.MapOfFinSets(native_factors[index], injection_graphs[index], native_apex),
        )
        for index in range(len(vertices))
    )

    def descent(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        target = cones.cocone_apex(candidate)
        native_target = _native_object_if_finite(target)
        if native_target is None:
            components = tuple(candidate.component(vertex) for vertex in vertices)
            return diagram.codomain().construct_morphism(apex, target, lambda tagged: _owned_map_value(components[tagged[0]], tagged[1]))
        tau = _native_components(candidate, vertices)
        computed = libgap.UniversalMorphismFromCoproductWithGivenCoproduct(category, native_factors, native_target, tau, computed_apex)
        return _native_map_on_owned_endpoints(apex, target, computed)

    return (
        diagram.codomain()
        .Colimits(diagram.domain())
        .with_universal_data(
            diagram,
            apex,
            cones.cocone(diagram, apex, lambda vertex: legs[positions[vertex]]),
            descent,
        )
    )


def _coequalizer(diagram: Functor, vertices: tuple[object, ...]) -> object:
    cones = _cones()

    arrows, source, target, category, native_maps = _parallel_pair_data(diagram)
    native_target = _native_object(target)
    computed_apex = libgap.Coequalizer(category, native_target, native_maps)
    computed_projection = libgap.ProjectionOntoCoequalizerWithGivenCoequalizer(category, native_target, native_maps, computed_apex)
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

    leg = _parallel_pair_leg(source_vertex, source_leg, target_leg)

    def descent(candidate: ConeCategory.ObjectType) -> MorphismCategory.ObjectType:
        candidate_target = cones.cocone_apex(candidate)
        candidate_native = _native_object_if_finite(candidate_target)
        component = candidate.component(target_vertex)
        if candidate_native is None:
            return diagram.codomain().construct_morphism(apex, candidate_target, lambda part: _owned_map_value(component, next(iter(part))))
        tau = _native_morphism(component)
        computed = libgap.UniversalMorphismFromCoequalizerWithGivenCoequalizer(
            category,
            native_target,
            native_maps,
            candidate_native,
            tau,
            computed_apex,
        )
        return _native_map_on_owned_endpoints(apex, candidate_target, computed)

    return diagram.codomain().Colimits(diagram.domain()).with_universal_data(diagram, apex, cones.cocone(diagram, apex, leg), descent)


def primitive_colimit(diagram: Functor) -> object:
    shape = diagram.domain()
    vertices = tuple(_finite_category_data(shape).objects)
    if shape.is_discrete():
        return _coproduct(diagram, vertices)
    return _coequalizer(diagram, vertices)
