"""Limits from products and equalizers, and the dual colimit construction.

Reference: Mathlib CategoryTheory.Limits.Constructions.LimitsOfProductsAndEqualizers.
The discrete indices can be arbitrary small sets. A finite presentation uses
its generators, since compatibility with generators implies compatibility
with every composite.
"""

from __future__ import annotations

__all__ = [
    "DiagramPresentation",
    "colimit_from_coproducts_coequalizers",
    "diagram_presentation",
    "limit_from_products_equalizers",
    "parallel_pair",
]

from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.cat.canonical import FinitePresentedCategory, _finite_discrete
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import (
    ConeCategory,
    LimitConesCategory,
    cone,
    cones,
    limit_cones,
)
from sage_categories.cat.constructions import constructed_data
from sage_categories.cat.diagrams import from_object_rule
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import OppositeCategory, opposite_morphism
from sage_categories.cat.predicates import Unknown, ask
from sage_categories.cat.shapes import Discrete
from sage_categories.kernel.retention import identity_key, identity_positions
from sage_categories.kernel.sage_runtime import cached_function


@dataclass(frozen=True)
class DiagramPresentation:
    """A discrete set of vertices, a discrete set of arrows, and incidence maps."""

    vertices: Functor
    source: Functor
    target: Functor
    arrows: NaturalTransformation


@cached_function(key=identity_key)
def diagram_presentation(shape: Category) -> DiagramPresentation:
    from sage_categories.cat.finite_categories import finite_category

    original = shape.original() if isinstance(shape, OppositeCategory) else shape
    finite = finite_category(shape) if not isinstance(original, FinitePresentedCategory) else Unknown
    if isinstance(original, FinitePresentedCategory) or finite is not Unknown:
        values = tuple(original(label) for label in original.labels()) if finite is Unknown else finite.objects
        generators = shape.generating_morphisms() if finite is Unknown else finite.morphisms
        generators = tuple(
            arrow for arrow in generators if arrow.domain() is not arrow.codomain() or ask(arrow == Mor(shape)(arrow.domain(), arrow.domain()).one()) is not True
        )
        vertices, edges = (
            _finite_discrete(len(values)),
            _finite_discrete(len(generators)),
        )
        positions = identity_positions(values)
        inclusion = from_object_rule(Fun(vertices, shape), lambda index: values[vertices.label(index)])

        def arrow_at(index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            return generators[edges.label(index)]

        source = from_object_rule(
            Fun(edges, vertices),
            lambda index: vertices(positions[arrow_at(index).domain()]),
        )
        target = from_object_rule(
            Fun(edges, vertices),
            lambda index: vertices(positions[arrow_at(index).codomain()]),
        )
    else:
        objects, morphisms = shape.object_set(), ask(shape.morphism_set())
        assert morphisms is not Unknown, "a small diagram requires its set of arrows"
        vertices, edges = Discrete(objects), Discrete(morphisms)
        inclusion = from_object_rule(Fun(vertices, shape), lambda index: shape.object_at(index.point()))

        def arrow_at(index: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            return shape.morphism_at(index.point())

        source = from_object_rule(
            Fun(edges, vertices),
            lambda index: vertices(shape.object_point(arrow_at(index).domain())),
        )
        target = from_object_rule(
            Fun(edges, vertices),
            lambda index: vertices(shape.object_point(arrow_at(index).codomain())),
        )
    arrows = Mor(Fun(edges, shape))(inclusion * source, inclusion * target)(arrow_at)
    return DiagramPresentation(inclusion, source, target, arrows)


@cached_function(key=identity_key)
def parallel_pair(first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType) -> Functor:
    """The parallel pair with its given common source and target."""
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    base, shape = first.base_category(), Cat().WalkingParallelPair()
    objects = (first.domain(), first.codomain())
    arrows = {"f": first, "g": second}
    return Fun(shape, base)(
        lambda vertex: objects[shape.label(vertex)],
        lambda arrow: (
            arrows[arrow.word()[0]]
            if arrow.word()
            else Mor(base)(
                objects[shape.label(arrow.domain())],
                objects[shape.label(arrow.domain())],
            ).one()
        ),
    )


type LimitChoice = Callable[[Functor], LimitConesCategory.ObjectType]


def _basis_parallel_maps(
    diagram: Functor,
    indexing: DiagramPresentation,
    objects: LimitConesCategory.ObjectType,
    targets: LimitConesCategory.ObjectType,
) -> tuple[MorphismCategory.ObjectType, MorphismCategory.ObjectType]:
    """The source/target maps whose equalizer imposes the diagram equations."""
    source_map = targets.lift(
        cones(targets.diagram())(
            cone(
                targets.diagram(),
                objects.apex(),
                lambda edge: diagram.on_morphism(indexing.arrows.component(edge)) * objects.leg(indexing.source.on_object(edge)),
            )
        )
    )
    target_map = targets.lift(
        cones(targets.diagram())(
            cone(
                targets.diagram(),
                objects.apex(),
                lambda edge: objects.leg(indexing.target.on_object(edge)),
            )
        )
    )
    return source_map, target_map


def _basis_index(
    diagram: Functor,
    indexing: DiagramPresentation,
    vertex: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    """The indexing-object representing one vertex of the original diagram."""
    indices = indexing.vertices.domain()
    if isinstance(indices, FinitePresentedCategory):
        return next(indices(label) for label in indices.labels() if ask(indexing.vertices.on_object(indices(label)) == vertex) is True)
    return indices(diagram.domain().object_point(vertex))


def _basis_lift(
    candidate: ConeCategory.ObjectType,
    *,
    indexing: DiagramPresentation,
    objects: LimitConesCategory.ObjectType,
    equalizer: LimitConesCategory.ObjectType,
    source_map: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    """Factor a candidate cone through the product/equalizer basis presentation."""
    into_product = objects.lift(
        cones(objects.diagram())(
            cone(
                objects.diagram(),
                candidate.apex(),
                lambda index: candidate.leg(indexing.vertices.on_object(index)),
            )
        )
    )
    maps = (into_product, source_map * into_product)
    return equalizer.lift(
        cones(equalizer.diagram())(
            cone(
                equalizer.diagram(),
                candidate.apex(),
                lambda vertex: maps[equalizer.diagram().domain().label(vertex)],
            )
        )
    )


def _basis_data(diagram: Functor, choose: LimitChoice, indexing: DiagramPresentation) -> LimitConesCategory.ObjectType:
    objects = choose(diagram * indexing.vertices)
    targets = choose(diagram * indexing.vertices * indexing.target)
    source_map, target_map = _basis_parallel_maps(diagram, indexing, objects, targets)
    equalizer = choose(parallel_pair(source_map, target_map))
    inclusion = equalizer.leg(0)

    presentation = cone(
        diagram,
        equalizer.apex(),
        lambda vertex: objects.leg(_basis_index(diagram, indexing, vertex)) * inclusion,
    )
    return limit_cones(diagram).with_universal_data(
        presentation,
        lambda candidate: _basis_lift(
            candidate,
            indexing=indexing,
            objects=objects,
            equalizer=equalizer,
            source_map=source_map,
        ),
    )


def limit_from_products_equalizers(
    diagram: Functor,
) -> CategoryOfCategories.ElementType:
    """Construct a limit using only discrete limits and a parallel-pair limit."""
    base = diagram.codomain()
    data = _basis_data(
        diagram,
        lambda part: constructed_data(base.Limits(part.domain()), part),
        diagram_presentation(diagram.domain()),
    )
    return base.Limits(diagram.domain()).with_presentation(data)


def colimit_from_coproducts_coequalizers(
    diagram: Functor,
) -> CategoryOfCategories.ElementType:
    """Construct a colimit with the dual product/equalizer universal maps."""
    base, dual = diagram.codomain(), diagram.op()

    def choose(part: Functor) -> LimitConesCategory.ObjectType:
        original = part.op()
        constructed_data(base.Colimits(original.domain()), original)
        return constructed_data(base.op().Limits(part.domain()), part)

    data = _basis_data(dual, choose, diagram_presentation(dual.domain()))
    lift = data._cone_lift
    return base.Colimits(diagram.domain()).with_universal_data(
        diagram,
        data.apex(),
        data.transformation().op(),
        lambda candidate: opposite_morphism(lift(cones(dual)(candidate.op()))),
    )
