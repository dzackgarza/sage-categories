"""Set-weighted limits and colimits through categories of elements.

Reference: Mathlib CategoryTheory.Limits.Weighted.HasWeightedLimit.
Ends are limits weighted by Hom; coends use its contravariant transpose.
Reference: Loregian, Coend calculus, sections 1.1 and 2.1.
"""

from __future__ import annotations

__all__ = [
    "element_projection",
    "Elements",
    "element",
    "weighted_limit",
    "weighted_colimit",
    "weighted_projection",
    "weighted_injection",
    "weighted_limit_lift",
    "weighted_colimit_desc",
    "weighted_limit_map",
    "weighted_colimit_map",
    "hom_functor",
    "yoneda",
    "coyoneda",
    "coend_weight",
    "end",
    "coend",
    "natural_transformation_diagram",
    "natural_transformation_to_end",
    "end_to_natural_transformation",
]

from collections.abc import Callable

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import cone, cocone, cones, cocones
from sage_categories.cat.constructions import constructed_data
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.indexed import Grothendieck, IndexedCategories
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown
from sage_categories.cat.shapes import discrete_functor
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

type WeightedComponents = Callable[
    [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType],
    MorphismCategory.ObjectType,
]


@cached_function(key=identity_key)
def element_projection(weight: Functor) -> Functor:
    """The discrete opfibration ``Elements(W) -> J`` of a covariant set functor."""
    discrete = discrete_functor(weight.codomain()) * weight
    indexed = IndexedCategories(weight.domain().op()).strict(discrete)
    return Grothendieck(indexed).projection().op()


def Elements(weight: Functor) -> Category:
    return element_projection(weight).domain()


def element(
    weight: Functor,
    vertex: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    """The object ``(j,x)`` of the category of elements."""
    total = Elements(weight).op()
    fiber = total.indexed_category().on_object(vertex)
    return total(vertex, fiber(point))


@cached_function(key=identity_key)
def _weighted_diagram(weight: Functor, diagram: Functor, dual: bool) -> Functor:
    projection = element_projection(weight)
    if dual:
        projection = projection.op()
    assert projection.codomain() is diagram.domain()
    return diagram * projection


def weighted_limit(
    weight: Functor, diagram: Functor
) -> CategoryOfCategories.ElementType:
    ordinary = _weighted_diagram(weight, diagram, False)
    return diagram.codomain().Limits(ordinary.domain())(ordinary)


def weighted_colimit(
    weight: Functor, diagram: Functor
) -> CategoryOfCategories.ElementType:
    ordinary = _weighted_diagram(weight, diagram, True)
    return diagram.codomain().Colimits(ordinary.domain())(ordinary)


def weighted_projection(
    weight: Functor,
    diagram: Functor,
    vertex: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, False)
    return constructed_data(diagram.codomain().Limits(ordinary.domain()), ordinary).leg(
        element(weight, vertex, point)
    )


def weighted_injection(
    weight: Functor,
    diagram: Functor,
    vertex: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, True)
    return constructed_data(
        diagram.codomain().Colimits(ordinary.domain()), ordinary
    ).leg(element(weight, vertex, point))


def weighted_limit_lift(
    weight: Functor,
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: WeightedComponents,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, False)
    data = constructed_data(diagram.codomain().Limits(ordinary.domain()), ordinary)
    return data.lift(
        cones(ordinary)(
            cone(
                ordinary,
                apex,
                lambda value: components(
                    value.base_object(), value.fiber_object().point()
                ),
            )
        )
    )


def weighted_colimit_desc(
    weight: Functor,
    diagram: Functor,
    apex: CategoryOfCategories.ElementType,
    components: WeightedComponents,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, True)
    data = constructed_data(diagram.codomain().Colimits(ordinary.domain()), ordinary)
    return data.lift(
        cocones(ordinary)(
            cocone(
                ordinary,
                apex,
                lambda value: components(
                    value.base_object(), value.fiber_object().point()
                ),
            )
        )
    )


def weighted_limit_map(
    weight: Functor, transformation: NaturalTransformation
) -> MorphismCategory.ObjectType:
    source, target = transformation.domain(), transformation.codomain()
    return weighted_limit_lift(
        weight,
        target,
        weighted_limit(weight, source),
        lambda vertex, point: (
            transformation.component(vertex)
            * weighted_projection(weight, source, vertex, point)
        ),
    )


def weighted_colimit_map(
    weight: Functor, transformation: NaturalTransformation
) -> MorphismCategory.ObjectType:
    source, target = transformation.domain(), transformation.codomain()
    return weighted_colimit_desc(
        weight,
        source,
        weighted_colimit(weight, target),
        lambda vertex, point: (
            weighted_injection(weight, target, vertex, point)
            * transformation.component(vertex)
        ),
    )


@cached_function(key=identity_key)
def hom_functor(category: Category, sets: Category) -> Functor:
    """The Hom functor using the category's chosen finite hom enumerations."""
    pairs = Cat().Products()((category.op(), category))

    def at(pair: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        arrows = category.hom_morphisms(pair.component(0), pair.component(1))
        assert arrows is not Unknown, "Hom evaluation requires an owned hom enumeration"
        return sets(arrows)

    result = Fun(pairs, sets)(
        at,
        lambda arrow: Mor(sets)(
            result.on_object(arrow.domain()), result.on_object(arrow.codomain())
        )(
            lambda value: (
                arrow.component(1) * value * opposite_morphism(arrow.component(0))
            )
        ),
    )
    return result


@cached_function(key=identity_key)
def yoneda(category: Category, sets: Category) -> Functor:
    """The covariant Yoneda embedding ``C -> Fun(C.op(), Sets)``."""
    from sage_categories.cat.calculus import curry, transpose

    from sage_categories.kernel.refinement import refine

    result = transpose(curry(hom_functor(category, sets)))
    refine(result, Fun.FullyFaithful())
    return result


@cached_function(key=identity_key)
def coyoneda(category: Category, sets: Category) -> Functor:
    """The covariant-hom embedding ``C.op() -> Fun(C, Sets)``."""
    from sage_categories.cat.calculus import curry
    from sage_categories.kernel.refinement import refine

    result = curry(hom_functor(category, sets))
    refine(result, Fun.FullyFaithful())
    return result


@cached_function(key=identity_key)
def coend_weight(hom: Functor) -> Functor:
    pairs = hom.domain()

    def swapped(
        pair: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return pairs((pair.component(1), pair.component(0)))

    def on_morphism(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        original = opposite_morphism(arrow)
        return hom.on_morphism(
            pairs.construct_morphism(
                swapped(arrow.domain()),
                swapped(arrow.codomain()),
                (
                    opposite_morphism(original.component(1)),
                    opposite_morphism(original.component(0)),
                ),
            )
        )

    return Fun(pairs.op(), hom.codomain())(
        lambda pair: hom.on_object(swapped(pair)), on_morphism
    )


def end(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType:
    """The end of ``D: J.op() × J -> C``, with its supplied Hom weight."""
    assert hom.domain() is diagram.domain()
    return weighted_limit(hom, diagram)


def coend(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType:
    """The coend of ``D: J.op() × J -> C``, with its supplied Hom weight."""
    assert hom.domain() is diagram.domain()
    return weighted_colimit(coend_weight(hom), diagram)


@cached_function(key=identity_key)
def natural_transformation_diagram(
    first: Functor, second: Functor, hom: Functor
) -> Functor:
    """The bifunctor ``(i,j) |-> Hom(F(i),G(j))``."""
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    source = Cat().Products()((first.domain().op(), first.domain()))
    target = hom.domain()
    images = Fun(source, target)(
        lambda pair: target(
            (first.on_object(pair.component(0)), second.on_object(pair.component(1)))
        ),
        lambda arrow: target.construct_morphism(
            target(
                (
                    first.on_object(arrow.domain().component(0)),
                    second.on_object(arrow.domain().component(1)),
                )
            ),
            target(
                (
                    first.on_object(arrow.codomain().component(0)),
                    second.on_object(arrow.codomain().component(1)),
                )
            ),
            (
                first.op().on_morphism(arrow.component(0)),
                second.on_morphism(arrow.component(1)),
            ),
        ),
    )
    return hom * images


def natural_transformation_to_end(
    transformation: NaturalTransformation, source_hom: Functor, target_hom: Functor
) -> CategoryOfCategories.ElementType:
    """The point of the Hom end specified by a natural transformation."""
    first, second = transformation.domain(), transformation.codomain()
    diagram = natural_transformation_diagram(first, second, target_hom)
    sets = target_hom.codomain()
    terminal = sets.Terminal()
    arrow = weighted_limit_lift(
        source_hom,
        diagram,
        terminal,
        lambda pair, point: Mor(sets)(terminal, diagram.on_object(pair))(
            lambda datum: (
                second.on_morphism(point.datum())
                * transformation.component(pair.component(0))
            )
        ),
    )
    return sets.element_from_defining_morphism(arrow)


def end_to_natural_transformation(
    point: CategoryOfCategories.ElementType,
    first: Functor,
    second: Functor,
    source_hom: Functor,
    target_hom: Functor,
) -> NaturalTransformation:
    """Recover a natural transformation from the diagonal projections of its Hom end."""
    diagram = natural_transformation_diagram(first, second, target_hom)
    assert point in end(diagram, source_hom)

    def component(
        vertex: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        pair = source_hom.domain()((vertex, vertex))
        identity = Mor(first.domain())(vertex, vertex).one()
        hom_point = source_hom.on_object(pair).point(identity)
        return weighted_projection(source_hom, diagram, pair, hom_point)(point).datum()

    return Mor(Fun(first.domain(), first.codomain()))(first, second)(component)
