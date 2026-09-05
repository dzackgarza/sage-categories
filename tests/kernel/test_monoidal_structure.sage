"""Coherence and nonidentity morphisms for supplied monoidal structures."""

from sage_categories.all import Cat, Fun, Mor, Sets, Cartesian, Composition, SelfAction, ask
from sage_categories.cat.monoidal import TrivialAction
from sage_categories.cat.structured_objects import Magmas, PointedMagmas, Monoids


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
    monoid = Monoids(structure)(multiplication, unit)
    assert monoid in Monoids(structure)
    assert monoid.carrier().carrier() is closure
    assert ask(monoid.unit_morphism().component(C(0)) == edge(0, 1)) is True
    assert monoid.unit_morphism().domain() is identity
    assert monoid.unit_morphism().codomain() is closure
    assert monoid.multiplication().component(C(2)).codomain() is C(2)
    assert Monoids(structure).to_magmas().on_object(monoid) is magma


test_cartesian_coherence()
test_composition_tensor()
