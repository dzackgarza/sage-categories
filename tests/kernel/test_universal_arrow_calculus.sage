"""Adjoint transposition, mates, and Kan adjunctions on nonidentity maps."""

from sage_categories.all import Adjunctions, Cat, Fun, Mor, ask
from sage_categories.all import (
    left_mate,
    right_mate,
    right_kan_adjunction,
    left_kan_adjunction,
)


def monotone(source, target, rule):
    def at(value):
        return target(rule(source.label(value)))

    def action(arrow):
        start, end = at(arrow.domain()), at(arrow.codomain())
        return target.construct_morphism(
            start,
            end,
            tuple(
                f"{i}->{i + 1}" for i in range(target.label(start), target.label(end))
            ),
        )

    return Fun(source, target)(at, action)


def test_mates_preserve_the_nonidentity_correspondence():
    first, second = Cat().Simplex(1), Cat().Simplex(2)
    left = monotone(first, second, lambda x: 2 * x)
    right = monotone(second, first, lambda x: x // 2)
    unit = Mor(Fun(first, first))(Fun(first, first).one(), right * left)(
        lambda value: Mor(first)(value, value).one()
    )
    counit = Mor(Fun(second, second))(left * right, Fun(second, second).one())(
        lambda value: second.construct_morphism(
            (left * right).on_object(value),
            value,
            tuple(
                f"{i}->{i + 1}"
                for i in range(
                    second.label((left * right).on_object(value)), second.label(value)
                )
            ),
        )
    )
    adjunction = Adjunctions(left, right)(unit, counit)
    top, bottom = Fun(first, first).constant(first(0)), Fun(second, second).one()
    alpha = Mor(Fun(first, second))(left * top, bottom * left)(
        lambda value: second.construct_morphism(
            second(0),
            left.on_object(value),
            tuple(f"{i}->{i + 1}" for i in range(second.label(left.on_object(value)))),
        )
    )
    beta = right_mate(adjunction, adjunction, top, bottom, alpha)
    assert ask(beta.component(second(2)) == first.generator("0->1")) is True
    restored = left_mate(adjunction, adjunction, top, bottom, beta)
    assert (
        ask(
            restored.component(first(1))
            == second.generator("1->2") * second.generator("0->1")
        )
        is True
    )


def test_kan_adjunction_functors_act_on_transformations():
    shape = Cat().Simplex(1)
    along = Fun(shape, shape).one()
    small, large = Cat().Simplex(0), Cat().Simplex(1)
    source, target = (
        Fun(shape, Cat()).constant(small),
        Fun(shape, Cat()).constant(large),
    )
    inclusion = Fun(small, large).constant(large(1))
    transformation = Mor(Fun(shape, Cat()))(source, target)(lambda vertex: inclusion)
    right = right_kan_adjunction(along, Cat())
    image = right.inverse().on_morphism(transformation)
    counit = right.counit().component(target)
    value = right.inverse().on_object(source).on_object(shape(0))
    unique = value(lambda vertex: small(0))
    assert counit.component(shape(0)).on_object(
        image.component(shape(0)).on_object(unique)
    ) is large(1)
    left = left_kan_adjunction(along, Cat())
    image = left.forward().on_morphism(transformation)
    injection = left.unit().component(source).component(shape(0))
    value = injection.on_object(small(0))
    assert image.component(shape(0)).on_object(value) in left.forward().on_object(
        target
    ).on_object(shape(0))


def test_pointwise_kan_adjunctions_in_finite_sets():
    from sage_categories.all import FiniteSets as sets

    shape, target = Cat().Simplex(1), Cat().Terminal()
    along = Fun(shape, target).constant(target(0))
    first, second = sets((0, 1)), sets((2,))
    collapse = Mor(sets)(first, second)(lambda value: 2)

    def at(vertex):
        return first if shape.label(vertex) == 0 else second

    diagram = Fun(shape, sets)(
        at,
        lambda arrow: (
            collapse
            if arrow.word()
            else Mor(sets)(at(arrow.domain()), at(arrow.domain())).one()
        ),
    )
    flip = Mor(sets)(first, first)(lambda value: 1 - value)
    transformation = Mor(Fun(shape, sets))(diagram, diagram)(
        lambda vertex: (
            flip if shape.label(vertex) == 0 else Mor(sets)(second, second).one()
        )
    )
    right, left = right_kan_adjunction(along, sets), left_kan_adjunction(along, sets)
    limit = right.inverse().on_object(diagram).on_object(target(0))
    projection = right.counit().component(diagram).component(shape(0))
    image = right.inverse().on_morphism(transformation).component(target(0))
    assert {projection(point).datum() for point in limit} == {0, 1}
    for point in limit:
        assert projection(image(point)).datum() == 1 - projection(point).datum()
    colimit = left.forward().on_object(diagram).on_object(target(0))
    assert len(tuple(colimit)) == 1
    injections = left.unit().component(diagram)
    assert (
        ask(
            injections.component(shape(0))(first.point(0))
            == injections.component(shape(1))(second.point(2))
        )
        is True
    )


test_mates_preserve_the_nonidentity_correspondence()
test_kan_adjunction_functors_act_on_transformations()
test_pointwise_kan_adjunctions_in_finite_sets()
