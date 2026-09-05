"""Presented pushouts and pointwise Kan universal maps through public consumers."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.cat.cones import cocone
from sage_categories.all import left_kan_extension, left_kan_unit, left_kan_desc
from sage_categories.all import right_kan_extension, right_kan_counit, right_kan_lift
from sage_categories.cat.diagrams import span_diagram
from sage_categories.cat.canonical import FinitePresentedCategory


def test_pushout_composes_arrows_from_both_factors() -> None:
    point, interval, triangle = Cat().Simplex(0), Cat().Simplex(1), Cat().Simplex(2)
    first = Fun(point, interval).constant(interval(1))
    second = Fun(point, interval).constant(interval(0))
    diagram = span_diagram(Cat(), first, second)
    result = Cat().Colimits(diagram.domain())(diagram)
    left, right = result.injection(1), result.injection(2)
    edge = interval.generator("0->1")
    assert left.on_object(interval(1)) is right.on_object(interval(0))
    composite = right.on_morphism(edge) * left.on_morphism(edge)
    assert composite.domain() is left.on_object(interval(0))
    assert composite.codomain() is right.on_object(interval(1))
    left_map = Fun(interval, triangle)(lambda value: triangle(interval.label(value)),
        lambda arrow: triangle.construct_morphism(triangle(interval.label(arrow.domain())), triangle(interval.label(arrow.codomain())), arrow.word()))
    right_map = Fun(interval, triangle)(lambda value: triangle(interval.label(value) + 1),
        lambda arrow: triangle.construct_morphism(triangle(interval.label(arrow.domain()) + 1), triangle(interval.label(arrow.codomain()) + 1), tuple("1->2" for name in arrow.word())))
    middle_map = Fun(point, triangle).constant(triangle(1))
    maps = (middle_map, left_map, right_map)
    mediator = result.universal_morphism(cocone(diagram, triangle, lambda vertex: maps[diagram.domain().label(vertex)]))
    assert ask(mediator.on_morphism(composite) == triangle.generator("1->2") * triangle.generator("0->1")) is True
    assert result.diagram() is diagram


def test_kan_maps_factor_nonidentity_transformations() -> None:
    base, fiber, larger = Cat().Simplex(1), Cat().Simplex(1), Cat().Simplex(2)
    along = Fun(base, base).one()
    identity = Fun(fiber, fiber).one()
    collapse = Fun(fiber, fiber).constant(fiber(0))
    diagram = Fun(base, Cat())(lambda vertex: fiber,
        lambda arrow: identity if arrow.domain() is arrow.codomain() else collapse)
    candidate = Fun(base, Cat()).constant(larger)
    to_fiber = tuple(Fun(larger, fiber).constant(fiber(i)) for i in (1, 0))
    transformation = Mor(Fun(base, Cat()))(candidate * along, diagram)(lambda vertex: to_fiber[base.label(vertex)])
    right = right_kan_extension(along, diagram)
    lift = right_kan_lift(along, diagram, candidate, transformation)
    counit = right_kan_counit(along, diagram)
    for vertex in (base(0), base(1)):
        value = lift.component(vertex).on_object(larger(2))
        assert counit.component(vertex).on_object(value) is transformation.component(vertex).on_object(larger(2))
    transported = right.on_morphism(base.generator("0->1")).on_object(lift.component(base(0)).on_object(larger(2)))
    assert counit.component(base(1)).on_object(transported) is fiber(0)

    inclusion = Fun(fiber, larger)(lambda value: larger(fiber.label(value)),
        lambda arrow: larger.construct_morphism(larger(fiber.label(arrow.domain())), larger(fiber.label(arrow.codomain())), arrow.word()))
    from_fiber = (Fun(fiber, larger).constant(larger(0)), inclusion)
    transformation = Mor(Fun(base, Cat()))(diagram, candidate * along)(lambda vertex: from_fiber[base.label(vertex)])
    left = left_kan_extension(along, diagram)
    descent = left_kan_desc(along, diagram, candidate, transformation)
    unit = left_kan_unit(along, diagram)
    for vertex in (base(0), base(1)):
        image = unit.component(vertex).on_morphism(fiber.generator("0->1"))
        assert ask(descent.component(vertex).on_morphism(image) == transformation.component(vertex).on_morphism(fiber.generator("0->1"))) is True
    transported = left.on_morphism(base.generator("0->1")).on_object(unit.component(base(0)).on_object(fiber(1)))
    assert descent.component(base(1)).on_object(transported) is larger(0)


def test_coequalizer_identifies_functor_images_of_a_generator() -> None:
    interval = Cat().Simplex(1)
    group = FinitePresentedCategory("B(C2)", (0,), (("s", 0, 0),), ((("s", "s"), ()),))
    identity = Mor(group)(group(0), group(0)).one()
    first = Fun(interval, group)(lambda vertex: group(0),
        lambda arrow: identity if not arrow.word() else group.generator("s"))
    second = Fun(interval, group).constant(group(0))
    shape = Cat().WalkingParallelPair()
    names = shape.generator_names()
    source, target = shape.generator(names[0]).domain(), shape.generator(names[0]).codomain()
    objects = {id(source): interval, id(target): group}
    maps = {names[0]: first, names[1]: second}
    diagram = Fun(shape, Cat())(lambda vertex: objects[id(vertex)],
        lambda arrow: Fun(objects[id(arrow.domain())], objects[id(arrow.domain())]).one() if not arrow.word() else maps[arrow.word()[0]])
    quotient = Cat().Colimits(shape)(diagram)
    injection = quotient.injection(target)
    image = injection.on_morphism(group.generator("s"))
    assert ask(image == Mor(quotient)(image.domain(), image.domain()).one()) is True
    assert injection.on_object(group(0)) in quotient


test_pushout_composes_arrows_from_both_factors()
test_kan_maps_factor_nonidentity_transformations()
test_coequalizer_identifies_functor_images_of_a_generator()
