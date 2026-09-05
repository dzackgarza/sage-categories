"""Cartesian closure, structured objects, and adjunction transposition."""

from sage_categories.all import Cat, Fun, Mor, ask
from sage_categories.cat.calculus import curry, uncurry, evaluation, currying, transpose
from sage_categories.cat.structured_objects import Inserter, EndofunctorAlgebras, EilenbergMoore
from sage_categories.cat.cones import cone, cones


def test_monoid_objects_receive_all_laws_from_equifiers():
    from sage_categories.sets import FiniteSets as sets
    from sage_categories.cat.calculus import product_functor
    from sage_categories.cat.structured_objects import Magmas, PointedMagmas, Monoids

    carrier = sets((0, 1, 2))
    tensor = product_functor(sets)
    multiplication = Mor(sets)(sets.Products()((carrier, carrier)), carrier)(
        lambda pair: (pair[0] + pair[1]) % 3
    )
    unit = Mor(sets)(sets.Terminal(), carrier)(lambda point: 0)
    magma = Magmas(tensor).algebra(carrier, multiplication)
    monoid = Monoids(sets)(multiplication, unit)
    assert (
        monoid.carrier().structure()(multiplication.domain().point((2, 2))).datum() == 1
    )
    automorphism = Mor(sets)(carrier, carrier)(lambda value: 2 * value % 3)
    magma_map = Magmas(tensor).homomorphism(magma, magma, automorphism)
    hom = PointedMagmas(tensor, sets.Terminal()).homomorphism(monoid, monoid, magma_map)
    assert (
        hom.underlying_morphism().underlying_morphism()(carrier.point(1)).datum() == 2
    )
    assert hom in Mor(Monoids(sets))(monoid, monoid)
    assert ask(hom * hom == Mor(Monoids(sets))(monoid, monoid).one()) is True
    from sage_categories.cat.monoidal import Cartesian, tensor_morphism

    wrong_unit = Mor(sets)(sets.Terminal(), carrier)(lambda point: 1)
    wrong_left_unit = multiplication * tensor_morphism(tensor, wrong_unit, Mor(sets)(carrier, carrier).one())
    assert ask(wrong_left_unit == Cartesian(sets).left_unitor().component(carrier)) is False


def test_cartesian_closure_transports_both_variables():
    interval, triangle = Cat().Simplex(1), Cat().Simplex(2)
    pairs = Cat().Products()((interval, interval))

    def image(pair):
        return triangle(
            interval.label(pair.family_component(0)) + interval.label(pair.family_component(1))
        )

    def arrow_image(arrow):
        start, end = image(arrow.domain()), image(arrow.codomain())
        return triangle.construct_morphism(
            start,
            end,
            tuple(
                f"{i}->{i + 1}"
                for i in range(triangle.label(start), triangle.label(end))
            ),
        )

    functor = Fun(pairs, triangle)(image, arrow_image)
    edge = interval.generator("0->1")
    square = pairs.construct_morphism(
        pairs((interval(0), interval(0))),
        pairs((interval(1), interval(1))),
        (edge, edge),
    )
    curried = curry(functor)
    assert curried.on_object(interval(1)).on_object(interval(1)) is triangle(2)
    assert (
        ask(
            uncurry(curried).on_morphism(square)
            == triangle.generator("1->2") * triangle.generator("0->1")
        )
        is True
    )
    assert (
        ask(
            curried.on_morphism(edge).component(interval(1))
            == triangle.generator("1->2")
        )
        is True
    )
    assert (
        ask(
            transpose(curried).on_morphism(edge).component(interval(0))
            == triangle.generator("0->1")
        )
        is True
    )
    evaluate = evaluation(interval, triangle)
    evaluation_pairs = evaluate.domain()
    value = evaluation_pairs((curried.on_object(interval(1)), interval(0)))
    assert evaluate.on_object(value) is triangle(1)
    equivalence = currying(interval, interval, triangle)
    comparison = equivalence.unit().component(functor)
    assert (
        ask(
            comparison.component(pairs((interval(1), interval(1))))
            == Mor(triangle)(triangle(2), triangle(2)).one()
        )
        is True
    )
    inverse = equivalence.unit().inverse().component(functor)
    assert (
        ask(
            (inverse * comparison).component(square.domain())
            == Mor(triangle)(triangle(0), triangle(0)).one()
        )
        is True
    )


def test_inserter_homomorphisms_and_monad_algebra_laws():
    base = Cat().Simplex(2)
    identity = Fun(base, base).one()
    constant = Fun(base, base).constant(base(0))
    category = Inserter(constant, identity)
    first = category.algebra(base(1), base.generator("0->1"))
    second = category.algebra(base(2), base.generator("1->2") * base.generator("0->1"))
    arrow = category.homomorphism(first, second, base.generator("1->2"))
    assert category.forgetful().on_morphism(arrow) is base.generator("1->2")
    assert category.defining_transformation().component(second) is second.structure()
    unit = Mor(Fun(base, base))(identity, identity).one()
    algebras = EndofunctorAlgebras(identity)
    em = EilenbergMoore(identity, unit, unit)
    value = algebras.algebra(base(2), Mor(base)(base(2), base(2)).one())
    em.ambient()(value)
    assert em(value).carrier() is base(2)


def test_limit_adjunction_transposes_a_competing_cone():
    shape, base = Cat().Simplex(1), Cat().Simplex(2)
    diagrams = Fun(shape, Cat())
    diagram = diagrams.constant(base)
    family = Cat().Limits(shape)
    adjunction = family.adjunction()
    source = Cat().Simplex(0)
    selected = Fun(source, base).constant(base(1))
    candidate = cone(diagram, source, lambda vertex: selected)
    arrow = adjunction.transpose(source, diagram, candidate)
    restored = adjunction.untranspose(source, diagram, arrow)
    for vertex in (shape(0), shape(1)):
        assert restored.component(vertex).on_object(source(0)) is base(1)


def test_pointing_monad_algebras_and_nonidentity_homomorphism():
    from sage_categories.all import FiniteSets as sets

    def pointed(carrier):
        return sets(((0, ()), *((1, point.datum()) for point in carrier)))

    def pointed_map(arrow):
        return Mor(sets)(pointed(arrow.domain()), pointed(arrow.codomain()))(
            lambda value: (
                (0, ())
                if value[0] == 0
                else (1, arrow(arrow.domain().point(value[1])).datum())
            )
        )

    monad = Fun(sets, sets)(pointed, pointed_map)
    unit = Mor(Fun(sets, sets))(Fun(sets, sets).one(), monad)(
        lambda carrier: Mor(sets)(carrier, pointed(carrier))(lambda value: (1, value))
    )
    multiplication = Mor(Fun(sets, sets))(monad * monad, monad)(
        lambda carrier: Mor(sets)(pointed(pointed(carrier)), pointed(carrier))(
            lambda value: (0, ()) if value[0] == 0 else value[1]
        )
    )
    algebras, em = EndofunctorAlgebras(monad), EilenbergMoore(monad, unit, multiplication)

    def algebra(carrier):
        action = Mor(sets)(pointed(carrier), carrier)(
            lambda value: 0 if value[0] == 0 else value[1]
        )
        return em(algebras.algebra(carrier, action))

    first, second = algebra(sets((0, 1))), algebra(sets((0, 1, 2)))
    arrow = Mor(sets)(first.carrier(), second.carrier())(lambda value: 2 * value)
    homomorphism = algebras.homomorphism(first, second, arrow)
    assert homomorphism in Mor(em)(first, second)
    assert homomorphism.underlying_morphism()(first.carrier().point(1)).datum() == 2
    assert first.structure()(pointed(first.carrier()).point((0, ()))).datum() == 0


test_cartesian_closure_transports_both_variables()
test_inserter_homomorphisms_and_monad_algebra_laws()
test_limit_adjunction_transposes_a_competing_cone()
test_monoid_objects_receive_all_laws_from_equifiers()
test_pointing_monad_algebras_and_nonidentity_homomorphism()
