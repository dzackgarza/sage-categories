"""Chosen set enumerations supply the vertices of a categorical product."""

from sage_categories.all import Cat, Discrete, Fun, Mor, Sets, ask
from sage_categories.cat.cones import cone, cones
from sage_categories.cat.declarations import NN
from sage_categories.cat.predicates import Unknown


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
    mediator = presentation.lift(cones(diagram)(candidate))
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


def test_product_enumeration_composes_the_chosen_factor_enumerations() -> None:
    colors, numbers = Sets(("red", "blue")), Sets((10, 20, 30))
    color_indices = Sets((7, 9))
    color_enumeration = Mor(Sets)(color_indices, colors).Isomorphisms()({7: "blue", 9: "red"})
    inclusion = Mor(Sets)(color_indices, NN).Monomorphisms()(lambda index: index)
    Sets.retain_enumeration(color_enumeration, inclusion)
    number_enumeration = Sets.chosen_enumeration(numbers)
    product = Sets.Products()((colors, numbers))
    enumeration = Sets.chosen_enumeration(product)
    indices = enumeration.domain()
    index_inclusion = Sets.enumeration_index_inclusion(enumeration)
    product_indices = Sets.Products()((color_indices, number_enumeration.domain()))
    index_enumeration = Sets.chosen_enumeration(product_indices)

    assert enumeration.codomain() is product
    assert index_inclusion.domain() is indices
    assert index_inclusion.codomain() is NN
    assert index_inclusion(indices.point(6)) is NN.point(6)
    assert enumeration(indices.point(1)) is product.point(("blue", 10))
    assert enumeration(indices.point(6)) is product.point(("red", 30))
    assert ask(product.product_projection(0) * enumeration == color_enumeration * product_indices.product_projection(0) * index_enumeration) is True
    assert ask(product.product_projection(1) * enumeration == number_enumeration * product_indices.product_projection(1) * index_enumeration) is True
    assert ask(enumeration.inverse() * enumeration == Mor(Sets)(indices, indices).one()) is True
    assert ask(enumeration * enumeration.inverse() == Mor(Sets)(product, product).one()) is True
    assert Sets.chosen_enumeration(colors) is color_enumeration
    assert Sets.enumeration_index_inclusion(color_enumeration) is inclusion
    assert Sets.chosen_enumeration(NN) is Unknown


test_discrete_owned_set_indexes_a_product_with_its_mediator()
test_product_enumeration_composes_the_chosen_factor_enumerations()
