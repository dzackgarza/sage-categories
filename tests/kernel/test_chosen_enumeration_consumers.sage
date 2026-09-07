"""Chosen set enumerations supply the vertices of a categorical product."""

from sage_categories.all import Cat, Discrete, Fun, Mor, Sets, ask
from sage_categories.cat.cones import cone


def test_discrete_owned_set_indexes_a_product_with_its_mediator() -> None:
    indices = Sets((0, 1))
    shape = Discrete(indices)
    first_vertex, second_vertex = shape(indices.point(0)), shape(indices.point(1))
    interval, triangle = Cat().Simplex(1), Cat().Simplex(2)
    diagram = Fun(shape, Cat()).from_object_rule(
        lambda vertex: interval if vertex is first_vertex else triangle
    )
    family = Cat().Limits(shape)
    product = family(diagram)
    presentation = family.universal_data(diagram)
    first_projection, second_projection = presentation.leg(first_vertex), presentation.leg(second_vertex)

    inclusion = Fun(interval, triangle)(
        lambda value: triangle(interval.label(value)),
        lambda arrow: Mor(triangle)(
            triangle(interval.label(arrow.domain())), triangle(interval.label(arrow.codomain()))
        )(arrow.word()),
    )
    identity = Fun(interval, interval).one()
    candidate = cone(diagram, interval, lambda vertex: identity if vertex is first_vertex else inclusion)
    mediator = presentation.lift(candidate)
    edge = interval.generator("0->1")
    image = mediator.on_morphism(edge)

    assert mediator.domain() is interval
    assert mediator.codomain() is product
    assert first_projection.on_object(mediator.on_object(interval(1))) is interval(1)
    assert second_projection.on_object(mediator.on_object(interval(1))) is triangle(1)
    assert ask(first_projection.on_morphism(image) == edge) is True
    assert ask(second_projection.on_morphism(image) == triangle.generator("0->1")) is True
    assert ask(first_projection * mediator == identity) is True
    assert ask(second_projection * mediator == inclusion) is True


test_discrete_owned_set_indexes_a_product_with_its_mediator()
