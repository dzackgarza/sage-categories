"""Weighted universal maps over a changing finite set weight."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.sets import FiniteSets as S
from sage_categories.cat.weighted import (
    weighted_limit,
    weighted_projection,
    weighted_limit_lift,
)
from sage_categories.cat.weighted import (
    weighted_colimit,
    weighted_injection,
    weighted_colimit_desc,
)
from sage_categories.cat.weighted import hom_functor, end, coend, yoneda
from sage_categories.cat.weighted import (
    natural_transformation_to_end,
    end_to_natural_transformation,
)
from sage_categories.cat.weighted import element_projection, element


def test_weighted_limit_and_colimit_have_nonconstant_transport():
    shape = Cat().Simplex(1)
    first, second = S((0, 1)), S((2,))
    collapse = Mor(S)(first, second)(lambda x: 2)
    weight = Fun(shape, S)(
        lambda vertex: first if shape.label(vertex) == 0 else second,
        lambda arrow: (
            collapse
            if arrow.word()
            else Mor(S)(
                first if shape.label(arrow.domain()) == 0 else second,
                first if shape.label(arrow.domain()) == 0 else second,
            ).one()
        ),
    )
    projection = element_projection(weight)
    assert projection in Fun(projection.domain(), shape).Opfibrations()
    source = element(weight, shape(0), first.point(1))
    lift = projection.cocartesian_lift(shape.generator("0->1"), source)
    assert lift.domain() is source
    assert lift.codomain() is element(weight, shape(1), second.point(2))
    assert ask(projection.on_morphism(lift) == shape.generator("0->1")) is True
    values = S((3, 4))
    diagram = Fun(shape, S).constant(values)
    limit = weighted_limit(weight, diagram)
    assert len(tuple(limit)) == 2
    maps = lambda vertex, point: Mor(S)(values, values).one()
    mediator = weighted_limit_lift(weight, diagram, values, maps)
    for value in values:
        assert (
            weighted_projection(weight, diagram, shape(0), first.point(1))(
                mediator(value)
            ).datum()
            == value.datum()
        )
    dual_weight = weight
    dual_diagram = Fun(shape.op(), S).constant(values)
    colimit = weighted_colimit(dual_weight, dual_diagram)
    assert len(tuple(colimit)) == 2
    desc = weighted_colimit_desc(dual_weight, dual_diagram, values, maps)
    for value in values:
        assert (
            desc(
                weighted_injection(
                    dual_weight, dual_diagram, shape(1), second.point(2)
                )(value)
            ).datum()
            == value.datum()
        )


def test_hom_weight_recovers_end_and_coend():
    shape = Cat().Simplex(1)
    hom = hom_functor(shape, S)
    values = S((0, 1))
    constant = Fun(hom.domain(), S).constant(values)
    assert len(tuple(end(constant, hom))) == 2
    assert len(tuple(coend(constant, hom))) == 2
    embedding = yoneda(shape, S)
    assert len(tuple(embedding.on_object(shape(0)).on_object(shape(1)))) == 0
    assert len(tuple(embedding.on_object(shape(1)).on_object(shape(0)))) == 1


def test_natural_transformations_are_points_of_the_hom_end():
    shape, target = Cat().Simplex(1), Cat().Simplex(2)
    first = Fun(shape, target)(
        lambda vertex: target(shape.label(vertex)),
        lambda arrow: (
            target.generator("0->1")
            if arrow.word()
            else Mor(target)(
                target(shape.label(arrow.domain())), target(shape.label(arrow.domain()))
            ).one()
        ),
    )
    second = Fun(shape, target)(
        lambda vertex: target(shape.label(vertex) + 1),
        lambda arrow: (
            target.generator("1->2")
            if arrow.word()
            else Mor(target)(
                target(shape.label(arrow.domain()) + 1),
                target(shape.label(arrow.domain()) + 1),
            ).one()
        ),
    )
    transformation = Mor(Fun(shape, target))(first, second)(
        lambda vertex: target.generator("0->1" if shape.label(vertex) == 0 else "1->2")
    )
    source_hom, target_hom = hom_functor(shape, S), hom_functor(target, S)
    point = natural_transformation_to_end(transformation, source_hom, target_hom)
    recovered = end_to_natural_transformation(
        point, first, second, source_hom, target_hom
    )
    assert ask(recovered.component(shape(0)) == target.generator("0->1")) is True
    assert ask(recovered.component(shape(1)) == target.generator("1->2")) is True


test_weighted_limit_and_colimit_have_nonconstant_transport()
test_hom_weight_recovers_end_and_coend()
test_natural_transformations_are_points_of_the_hom_end()
