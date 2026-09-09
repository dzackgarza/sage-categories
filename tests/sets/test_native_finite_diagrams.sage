from sympy import Q

from sage_categories.all import Cat, Fun, Mor, Sets, ask
from sage_categories.cat.cones import cocone, cocones, cone, cones


def test_native_finite_limit_and_colimit_over_three_vertices() -> None:
    shape = Cat().Simplex(2)
    v0, v1, v2 = (shape(i) for i in range(3))
    A = Sets(("a0", "a1"))
    B = Sets(("b0", "b1", "b2"))
    C = Sets(("c0", "c1"))
    f = Mor(Sets)(A, B)({"a0": "b0", "a1": "b1"})
    g = Mor(Sets)(B, C)({"b0": "c0", "b1": "c1", "b2": "c1"})
    objects = (A, B, C)

    def on_object(vertex):
        return objects[shape.label(vertex)]

    def on_morphism(arrow):
        source = shape.label(arrow.domain())
        target = shape.label(arrow.codomain())
        if source == target:
            return Mor(Sets)(objects[source], objects[source]).one()
        if (source, target) == (0, 1):
            return f
        if (source, target) == (1, 2):
            return g
        assert (source, target) == (0, 2)
        return g * f

    diagram = Fun(shape, Sets)(on_object, on_morphism)
    limit = Sets.Limits(shape)(diagram)
    selected_limit = Sets.Limits(shape).universal_data(diagram)
    assert {point.datum() for point in limit} == {
        ("a0", "b0", "c0"),
        ("a1", "b1", "c1"),
    }
    source = Sets(("x", "y"))
    to_a = Mor(Sets)(source, A)({"x": "a0", "y": "a1"})
    candidate = cone(
        diagram,
        source,
        lambda vertex: to_a if vertex is v0 else f * to_a if vertex is v1 else g * f * to_a,
    )
    lift = selected_limit.lift(cones(diagram)(candidate))
    assert ask(selected_limit.leg(0) * lift == to_a) is True

    integers = Sets.from_membership(lambda value: Q.integer(value))
    infinite_to_a = Mor(Sets)(integers, A)(lambda value: "a0" if value % 2 == 0 else "a1")
    infinite_candidate = cone(
        diagram,
        integers,
        lambda vertex: infinite_to_a
        if vertex is v0
        else f * infinite_to_a
        if vertex is v1
        else g * f * infinite_to_a,
    )
    infinite_lift = selected_limit.lift(cones(diagram)(infinite_candidate))
    assert infinite_lift(integers.point(2)).datum() == ("a0", "b0", "c0")
    assert infinite_lift(integers.point(3)).datum() == ("a1", "b1", "c1")

    colimit = Sets.Colimits(shape)(diagram)
    selected_colimit = Sets.Colimits(shape).universal_data(diagram)
    assert len(tuple(colimit)) == 2
    target = Sets((0, 1))
    from_c = Mor(Sets)(C, target)({"c0": 0, "c1": 1})
    candidate = cocone(
        diagram,
        target,
        lambda vertex: from_c * g * f if vertex is v0 else from_c * g if vertex is v1 else from_c,
    )
    descent = selected_colimit.lift(cocones(diagram)(candidate))
    assert ask(descent * selected_colimit.leg(2) == from_c) is True

    infinite_from_c = Mor(Sets)(C, integers)({"c0": 10, "c1": 11})
    infinite_candidate = cocone(
        diagram,
        integers,
        lambda vertex: infinite_from_c * g * f
        if vertex is v0
        else infinite_from_c * g
        if vertex is v1
        else infinite_from_c,
    )
    infinite_descent = selected_colimit.lift(cocones(diagram)(infinite_candidate))
    assert infinite_descent(selected_colimit.leg(2)(C.point("c0"))).datum() == 10
    assert infinite_descent(selected_colimit.leg(2)(C.point("c1"))).datum() == 11


test_native_finite_limit_and_colimit_over_three_vertices()
