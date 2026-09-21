"""Set-weighted limits and colimits through categories of elements.

Reference: Mathlib CategoryTheory.Limits.Weighted.HasWeightedLimit.
Ends are limits weighted by Hom; coends use its contravariant transpose.
Reference: Loregian, Coend calculus, sections 1.1 and 2.1.
"""

from __future__ import annotations

__all__ = [
    "Elements",
    "coend",
    "coend_weight",
    "coyoneda",
    "element",
    "element_projection",
    "end",
    "end_to_natural_transformation",
    "hom_functor",
    "natural_transformation_diagram",
    "natural_transformation_to_end",
    "restricted_yoneda",
    "separating_evaluation",
    "separating_evaluation_injection",
    "weighted_colimit",
    "weighted_colimit_desc",
    "weighted_colimit_map",
    "weighted_injection",
    "weighted_limit",
    "weighted_limit_lift",
    "weighted_limit_map",
    "weighted_projection",
    "yoneda",
]

from collections.abc import Callable
from types import ModuleType

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import cocone, cocones, cone, cones
from sage_categories.cat.constructions import UniversalPresentation, constructed_data
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.indexed import Grothendieck, IndexedCategories
from sage_categories.cat.morphisms import Mor, MorphismCategory
from sage_categories.cat.opposites import opposite_morphism
from sage_categories.cat.predicates import Unknown
from sage_categories.cat.shapes import discrete_functor
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function

type WeightedComponents = Callable[
    [CategoryOfCategories.ElementType, CategoryOfCategories.ElementType],
    MorphismCategory.ObjectType,
]


def _calculus() -> ModuleType:
    """Load curry/transpose at the cycle-safe weighted/calculus boundary."""
    from sage_categories.cat import calculus

    return calculus


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


def weighted_limit(weight: Functor, diagram: Functor) -> CategoryOfCategories.ElementType:
    ordinary = _weighted_diagram(weight, diagram, False)
    return diagram.codomain().Limits(ordinary.domain())(ordinary)


def weighted_colimit(weight: Functor, diagram: Functor) -> CategoryOfCategories.ElementType:
    ordinary = _weighted_diagram(weight, diagram, True)
    return diagram.codomain().Colimits(ordinary.domain())(ordinary)


def weighted_projection(
    weight: Functor,
    diagram: Functor,
    vertex: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, False)
    return constructed_data(diagram.codomain().Limits(ordinary.domain()), ordinary).leg(element(weight, vertex, point))


def weighted_injection(
    weight: Functor,
    diagram: Functor,
    vertex: CategoryOfCategories.ElementType,
    point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    ordinary = _weighted_diagram(weight, diagram, True)
    return constructed_data(diagram.codomain().Colimits(ordinary.domain()), ordinary).leg(element(weight, vertex, point))


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
                lambda value: components(value.base_object(), value.fiber_object().point()),
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
                lambda value: components(value.base_object(), value.fiber_object().point()),
            )
        )
    )


def weighted_limit_map(weight: Functor, transformation: NaturalTransformation) -> MorphismCategory.ObjectType:
    source, target = transformation.domain(), transformation.codomain()
    return weighted_limit_lift(
        weight,
        target,
        weighted_limit(weight, source),
        lambda vertex, point: transformation.component(vertex) * weighted_projection(weight, source, vertex, point),
    )


def weighted_colimit_map(weight: Functor, transformation: NaturalTransformation) -> MorphismCategory.ObjectType:
    source, target = transformation.domain(), transformation.codomain()
    return weighted_colimit_desc(
        weight,
        source,
        weighted_colimit(weight, target),
        lambda vertex, point: weighted_injection(weight, target, vertex, point) * transformation.component(vertex),
    )


@cached_function(key=identity_key)
def hom_functor(category: Category, sets: Category) -> Functor:
    """The Hom functor using the category's chosen finite hom enumerations."""
    pairs = Cat().Products()((category.op(), category))

    def at(pair: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        arrows = category.hom_morphisms(pair.family_component(0), pair.family_component(1))
        assert arrows is not Unknown, "Hom evaluation requires an owned hom enumeration"
        return sets(arrows)

    result = Fun(pairs, sets)(
        at,
        lambda arrow: Mor(sets)(result.on_object(arrow.domain()), result.on_object(arrow.codomain()))(
            lambda value: arrow.family_component(1) * value * opposite_morphism(arrow.family_component(0))
        ),
    )
    return result


@cached_function(key=identity_key)
def yoneda(category: Category, sets: Category) -> Functor:
    """The covariant Yoneda embedding ``C -> Fun(C.op(), Sets)``."""
    return _yoneda_from_hom(hom_functor(category, sets))


@cached_function(key=identity_key)
def _yoneda_from_hom(hom: Functor) -> Functor:
    """The Yoneda embedding built from a supplied Hom bifunctor.

    Supplying the Hom functor separates the mathematical construction from any
    finite enumeration used by :func:`hom_functor`.
    """
    pairs = hom.domain()
    category = pairs.factor(1)
    assert pairs.factor(0) is category.op(), f"{hom!r} does not have domain C.op() * C"
    calculus = _calculus()
    result = calculus.transpose(calculus.curry(hom))
    refine(result, Fun.FullyFaithful())
    return result


@cached_function(key=identity_key)
def coyoneda(category: Category, sets: Category) -> Functor:
    """The covariant-hom embedding ``C.op() -> Fun(C, Sets)``."""
    result = _calculus().curry(hom_functor(category, sets))
    refine(result, Fun.FullyFaithful())
    return result


@cached_function(key=identity_key)
def restricted_yoneda(test: Functor, hom: Functor) -> Functor:
    """The restricted Yoneda functor along ``test: A -> C``.

    The supplied ``hom: C.op() * C -> S`` may represent its Hom sets without
    finite enumeration.  The result is ``C -> Fun(A.op(), S)``.
    """
    embedding = _yoneda_from_hom(hom)
    assert embedding.domain() is test.codomain(), f"{hom!r} is not the Hom bifunctor of {test.codomain()!r}"
    return _calculus().precompose(test.op(), hom.codomain()) * embedding


def _probe_object(
    test: Functor,
    vertex: CategoryOfCategories.ElementType,
) -> CategoryOfCategories.ElementType:
    return test.domain().object_at(vertex.point())


@cached_function(key=identity_key)
def _probe_copower_diagram(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
    probe: CategoryOfCategories.ElementType,
) -> Functor:
    nerve = restricted_yoneda(test, hom)
    hom_set = nerve.on_object(value).on_object(probe)
    shape = discrete_functor(hom.codomain()).on_object(hom_set)
    return Fun(shape, test.codomain()).constant(test.on_object(probe))


@cached_function(key=identity_key)
def _probe_copower_data(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
    probe: CategoryOfCategories.ElementType,
) -> UniversalPresentation:
    diagram = _probe_copower_diagram(test, hom, value, probe)
    family = test.codomain().Colimits(diagram.domain())
    family(diagram)
    return constructed_data(family, diagram)


@cached_function(key=identity_key)
def _probe_evaluation_diagram(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
) -> Functor:
    shape = discrete_functor(hom.codomain()).on_object(test.domain().object_set())
    return Fun(shape, test.codomain()).from_object_rule(
        lambda vertex: _probe_copower_data(
            test,
            hom,
            value,
            _probe_object(test, vertex),
        ).apex()
    )


@cached_function(key=identity_key)
def _probe_evaluation_data(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
) -> UniversalPresentation:
    diagram = _probe_evaluation_diagram(test, hom, value)
    family = test.codomain().Colimits(diagram.domain())
    family(diagram)
    return constructed_data(family, diagram)


def _probe_evaluation_map(
    test: Functor,
    hom: Functor,
    arrow: MorphismCategory.ObjectType,
) -> MorphismCategory.ObjectType:
    source = _probe_evaluation_data(test, hom, arrow.domain())
    target = _probe_evaluation_data(test, hom, arrow.codomain())
    nerve_map = restricted_yoneda(test, hom).on_morphism(arrow)

    def outer_component(
        vertex: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        probe = _probe_object(test, vertex)
        source_inner = _probe_copower_data(test, hom, arrow.domain(), probe)
        target_inner = _probe_copower_data(test, hom, arrow.codomain(), probe)

        def inner_component(
            inner_vertex: CategoryOfCategories.ElementType,
        ) -> MorphismCategory.ObjectType:
            target_point = nerve_map.component(probe)(inner_vertex.point())
            target_vertex = target_inner.diagram().domain().object_at(target_point)
            return target.leg(vertex) * target_inner.leg(target_vertex)

        candidate = cocone(
            source_inner.diagram(),
            target.apex(),
            inner_component,
        )
        return source_inner.lift(cocones(source_inner.diagram())(candidate))

    candidate = cocone(source.diagram(), target.apex(), outer_component)
    return source.lift(cocones(source.diagram())(candidate))


@cached_function(key=identity_key)
def _probe_evaluation_functor(test: Functor, hom: Functor) -> Functor:
    base = test.codomain()
    return Fun(base, base)(
        lambda value: _probe_evaluation_data(test, hom, value).apex(),
        lambda arrow: _probe_evaluation_map(test, hom, arrow),
    )


def _probe_evaluation_component(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    outer = _probe_evaluation_data(test, hom, value)

    def outer_component(
        vertex: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        probe = _probe_object(test, vertex)
        inner = _probe_copower_data(test, hom, value, probe)
        candidate = cocone(
            inner.diagram(),
            value,
            lambda inner_vertex: inner_vertex.point().datum(),
        )
        return inner.lift(cocones(inner.diagram())(candidate))

    candidate = cocone(outer.diagram(), value, outer_component)
    return outer.lift(cocones(outer.diagram())(candidate))


@cached_function(key=identity_key)
def separating_evaluation(test: Functor, hom: Functor) -> NaturalTransformation:
    """The canonical evaluation epimorphism for a separating test functor.

    Its source functor sends ``X`` to the coproduct of one copy of ``j(a)``
    for every pair ``(a, u: j(a) -> X)``.  Both coproducts may have
    nonenumerable represented index sets.
    """
    nerve = restricted_yoneda(test, hom)
    assert nerve in Fun.Faithful(), f"{test!r} is not retained as separating: its restricted Yoneda functor is not retained as faithful"
    base = test.codomain()
    source = _probe_evaluation_functor(test, hom)
    target = Fun(base, base).one()

    def component(
        value: CategoryOfCategories.ElementType,
    ) -> MorphismCategory.ObjectType:
        arrow = _probe_evaluation_component(test, hom, value)
        refine(arrow, Mor(base).Epimorphisms())
        return arrow

    return Mor(Fun(base, base))(source, target)(component)


def separating_evaluation_injection(
    test: Functor,
    hom: Functor,
    value: CategoryOfCategories.ElementType,
    probe_point: CategoryOfCategories.ElementType,
    hom_point: CategoryOfCategories.ElementType,
) -> MorphismCategory.ObjectType:
    """The canonical summand injection indexed by ``(a, u: j(a) -> X)``."""
    evaluation = separating_evaluation(test, hom)
    outer = _probe_evaluation_data(test, hom, value)
    outer_vertex = outer.diagram().domain().object_at(probe_point)
    probe = test.domain().object_at(probe_point)
    inner = _probe_copower_data(test, hom, value, probe)
    inner_vertex = inner.diagram().domain().object_at(hom_point)
    injection = outer.leg(outer_vertex) * inner.leg(inner_vertex)
    assert injection.codomain() is evaluation.domain().on_object(value)
    return injection


@cached_function(key=identity_key)
def coend_weight(hom: Functor) -> Functor:
    pairs = hom.domain()

    def swapped(
        pair: CategoryOfCategories.ElementType,
    ) -> CategoryOfCategories.ElementType:
        return pairs((pair.family_component(1), pair.family_component(0)))

    def on_morphism(arrow: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        original = opposite_morphism(arrow)
        return hom.on_morphism(
            pairs.construct_morphism(
                swapped(arrow.domain()),
                swapped(arrow.codomain()),
                (
                    opposite_morphism(original.family_component(1)),
                    opposite_morphism(original.family_component(0)),
                ),
            )
        )

    return Fun(pairs.op(), hom.codomain())(lambda pair: hom.on_object(swapped(pair)), on_morphism)


def end(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType:
    """The end of ``D: J.op() × J -> C``, with its supplied Hom weight."""
    assert hom.domain() is diagram.domain()
    return weighted_limit(hom, diagram)


def coend(diagram: Functor, hom: Functor) -> CategoryOfCategories.ElementType:
    """The coend of ``D: J.op() × J -> C``, with its supplied Hom weight."""
    assert hom.domain() is diagram.domain()
    return weighted_colimit(coend_weight(hom), diagram)


@cached_function(key=identity_key)
def natural_transformation_diagram(first: Functor, second: Functor, hom: Functor) -> Functor:
    """The bifunctor ``(i,j) |-> Hom(F(i),G(j))``."""
    assert first.domain() is second.domain() and first.codomain() is second.codomain()
    source = Cat().Products()((first.domain().op(), first.domain()))
    target = hom.domain()
    images = Fun(source, target)(
        lambda pair: target((first.on_object(pair.family_component(0)), second.on_object(pair.family_component(1)))),
        lambda arrow: target.construct_morphism(
            target(
                (
                    first.on_object(arrow.domain().family_component(0)),
                    second.on_object(arrow.domain().family_component(1)),
                )
            ),
            target(
                (
                    first.on_object(arrow.codomain().family_component(0)),
                    second.on_object(arrow.codomain().family_component(1)),
                )
            ),
            (
                first.op().on_morphism(arrow.family_component(0)),
                second.on_morphism(arrow.family_component(1)),
            ),
        ),
    )
    return hom * images


def natural_transformation_to_end(transformation: NaturalTransformation, source_hom: Functor, target_hom: Functor) -> CategoryOfCategories.ElementType:
    """The point of the Hom end specified by a natural transformation."""
    first, second = transformation.domain(), transformation.codomain()
    diagram = natural_transformation_diagram(first, second, target_hom)
    sets = target_hom.codomain()
    terminal = sets.Terminal()
    arrow = weighted_limit_lift(
        source_hom,
        diagram,
        terminal,
        lambda pair, point: Mor(sets)(terminal, diagram.on_object(pair))(lambda datum: second.on_morphism(point.datum()) * transformation.component(pair.family_component(0))),
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
