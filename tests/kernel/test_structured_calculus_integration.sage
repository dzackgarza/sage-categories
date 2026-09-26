"""Indexed, weighted, and algebraic calculus interoperate through their public owners."""

from sage_categories.all import Cat, Fun, Mor, Sets, ask
from sage_categories.cat.calculus import binary_product_data, pair_maps
from sage_categories.cat.monoidal import Cartesian
from sage_categories.cat.structured_objects import Monoids
from sage_categories.cat.weighted import (
    element_projection,
    weighted_limit,
    weighted_limit_lift,
    weighted_projection,
)
from sage_categories.sets import FiniteSets


def test_weighted_limit_supplies_an_internal_monoid() -> None:
    """A Grothendieck-indexed weighted product supplies componentwise monoid structure."""
    carrier = Sets((0, 1))
    cartesian = Cartesian(Sets())
    carrier_square = binary_product_data(Sets(), carrier, carrier).apex()
    conjunction = Mor(Sets)(carrier_square, carrier)(lambda pair: min(pair))
    one = Mor(Sets)(cartesian.unit(), carrier)(lambda _point: 1)
    monoids = Monoids(cartesian)
    boolean = monoids(conjunction, one)

    shape = Cat().Terminal()
    vertex = shape(0)
    weight_values = FiniteSets((0, 1))
    weight = Fun(shape, FiniteSets).constant(weight_values)
    elements = element_projection(weight)
    assert elements in Fun(elements.domain(), shape).Opfibrations()

    diagram = Fun(shape, Sets()).constant(carrier)
    limit = weighted_limit(weight, diagram)
    square = binary_product_data(Sets(), limit, limit)

    def multiplication_component(_vertex, point):
        projection = weighted_projection(weight, diagram, vertex, point)
        return conjunction * pair_maps(
            Sets(),
            projection * square.leg(0),
            projection * square.leg(1),
        )

    multiplication = weighted_limit_lift(
        weight,
        diagram,
        square.apex(),
        multiplication_component,
    )
    unit = weighted_limit_lift(
        weight,
        diagram,
        cartesian.unit(),
        lambda _vertex, _point: one,
    )
    product_monoid = monoids(multiplication, unit)
    assert product_monoid.operation().codomain() is limit

    for point in (weight_values.point(0), weight_values.point(1)):
        projection = weighted_projection(weight, diagram, vertex, point)
        monoid_projection = monoids.homomorphism(product_monoid, boolean, projection)
        assert monoid_projection in Mor(monoids)(product_monoid, boolean)
        assert monoids.to_magmas().on_morphism(monoid_projection).underlying_morphism() is projection

    first = weighted_projection(weight, diagram, vertex, weight_values.point(0))
    second = weighted_projection(weight, diagram, vertex, weight_values.point(1))
    assert ask(first == second) is False


test_weighted_limit_supplies_an_internal_monoid()
