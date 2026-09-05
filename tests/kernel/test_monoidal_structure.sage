"""Coherence and nonidentity morphisms for supplied monoidal structures."""

from sage_categories.all import Cat, Fun, Mor, Sets, Cartesian, Composition, SelfAction, ask
from sage_categories.cat.monoidal import TrivialAction
from sage_categories.cat.structured_objects import Magmas, Monoids


def test_functor_and_transformation_equality() -> None:
    source, target = Cat().Terminal(), Cat().WalkingParallelPair()
    diagrams = Fun(source, target)
    first = diagrams.constant(target(0))
    same = diagrams(lambda vertex: target(0), lambda arrow: Mor(target)(target(0), target(0)).one())
    second = diagrams.constant(target(1))
    assert ask(first == same) is True
    assert ask(first == second) is False
    transformations = Mor(diagrams)(first, second)
    alpha = transformations(lambda vertex: target.generator("f"))
    beta = transformations(lambda vertex: target.generator("g"))
    duplicate = transformations(lambda vertex: target.generator("f"))
    assert ask(alpha == duplicate) is True
    assert ask(alpha == beta) is False


def test_cartesian_coherence() -> None:
    structure = Cartesian(Sets)
    X, Y, Z, W = (Sets(values) for values in ((0, 1), (2, 3), (4, 5), (6, 7)))
    triples = structure.associator().domain().domain()
    alpha = structure.associator().component(triples((X, Y, Z)))
    point = alpha.domain().point(((1, 2), 5))
    assert alpha(point).datum() == (1, (2, 5))
    assert alpha(point).parent() is alpha.codomain()
    assert alpha.inverse()(alpha(point)).datum() == ((1, 2), 5)
    for unitor, datum in ((structure.left_unitor(), ((), 1)), (structure.right_unitor(), (1, ()))):
        component = unitor.component(X)
        assert component(component.domain().point(datum)).datum() == 1
        assert component.codomain() is X
        assert component.inverse()(X.point(1)).datum() == datum
    assert ask(structure.pentagon(W, X, Y, Z)) is True
    assert ask(structure.triangle(X, Y)) is True

    action = SelfAction(structure)
    f = Mor(Sets)(X, Y)(lambda n: n + 2)
    g = Mor(Sets)(Y, Z)(lambda n: n + 2)
    pairs = action.action().domain()
    image = action.action().on_morphism(Mor(pairs)(pairs((X, Y)), pairs((Y, Z)))((f, g)))
    assert image(image.domain().point((1, 2))).datum() == (3, 4)
    assert action.unitor().component(X).codomain() is X
    assert ask(action.pentagon(W, X, Y, Z)) is True
    assert ask(action.triangle(X, Y)) is True
    trivial = TrivialAction(structure, Sets)
    assert trivial is not action
    assert trivial.action().on_object(pairs((X, Y))) is Y
    assert trivial.action().on_morphism(Mor(pairs)(pairs((X, Y)), pairs((Y, Z)))((f, g))) is g
    assert trivial.unitor().component(X)(X.point(1)).datum() == 1


def test_composition_tensor() -> None:
    C = Cat().Simplex(2)
    E = Fun(C, C)
    identity, bottom, top = E.one(), E.constant(C(0)), E.constant(C(2))
    edge = lambda i, j: Mor(C)(C(i), C(j))(tuple(f"{k}->{k + 1}" for k in range(i, j)))
    theta = Mor(E)(identity, top)(lambda x: edge(C.label(x), 2))
    eta = Mor(E)(bottom, identity)(lambda x: edge(0, C.label(x)))
    structure = Composition(C)
    pairs = structure.tensor().domain()
    arrow = Mor(pairs)(pairs((identity, bottom)), pairs((top, identity)))((theta, eta))
    composite = structure.tensor().on_morphism(arrow)
    assert ask(composite.component(C(1)) == edge(0, 2)) is True
    assert structure.unit() is identity
    assert structure.unit().on_object(C(0)) is C(0)
    assert top.on_object(C(0)) is C(2)
    action = SelfAction(structure)
    assert ask(action.action().on_morphism(arrow).component(C(1)) == edge(0, 2)) is True
    assert action.unitor().component(bottom).component(C(1)).domain() is C(0)

    closure = E(lambda x: C(max(1, C.label(x))),
        lambda f: edge(max(1, C.label(f.domain())), max(1, C.label(f.codomain()))))
    multiplication = Mor(E)(closure * closure, closure)(lambda x: edge(max(1, C.label(x)), max(1, C.label(x))))
    unit = Mor(E)(identity, closure)(lambda x: edge(C.label(x), max(1, C.label(x))))
    magma = Magmas(structure).algebra(closure, multiplication)
    assert magma.on_object(C(0)) is closure.on_object(C(0))
    assert magma.domain() is C and magma.codomain() is C
    assert ask(magma.on_morphism(edge(0, 2)) == edge(1, 2)) is True
    top_multiplication = Mor(E)(top * top, top)(lambda x: edge(2, 2))
    top_magma = Magmas(structure).algebra(top, top_multiplication)
    comparison = Mor(E)(closure, top)(lambda x: edge(max(1, C.label(x)), 2))
    magma_map = Magmas(structure).homomorphism(magma, top_magma, comparison)
    assert ask(Magmas(structure).forgetful().on_morphism(magma_map).component(C(1)) == edge(1, 2)) is True
    monoid = Monoids(structure)(multiplication, unit)
    assert monoid in Monoids(structure)
    assert monoid.carrier().carrier() is closure
    assert ask(monoid.unit_morphism().component(C(0)) == edge(0, 1)) is True
    assert monoid.unit_morphism().domain() is identity
    assert monoid.unit_morphism().codomain() is closure
    assert monoid.multiplication().component(C(2)).codomain() is C(2)
    assert Monoids(structure).to_magmas().on_object(monoid) is magma


def test_closure_monad_on_two_element_chain() -> None:
    interval = Cat().Simplex(1)
    endofunctors = Fun(interval, interval)
    identity = endofunctors.one()
    closure = endofunctors.constant(interval(1))
    edge = interval.generator("0->1")
    identity_at_top = Mor(interval)(interval(1), interval(1)).one()
    unit = Mor(endofunctors)(identity, closure)(
        lambda vertex: edge if interval.label(vertex) == 0 else identity_at_top
    )
    multiplication = Mor(endofunctors)(closure * closure, closure)(
        lambda vertex: identity_at_top
    )
    structure = Composition(interval)
    monad = Monoids(structure)(multiplication, unit)
    assert monad in Monoids(structure)
    assert structure.unit() is identity
    assert ask(identity == endofunctors.Terminal()) is False
    assert ask(monad.unit_morphism().component(interval(0)) == edge) is True
    assert monad.multiplication().component(interval(0)).domain() is interval(1)
    assert monad.multiplication().component(interval(0)).codomain() is interval(1)


test_functor_and_transformation_equality()
test_cartesian_coherence()
test_composition_tensor()
test_closure_monad_on_two_element_chain()
