"""Owned set maps, universal maps, and represented infinite sets."""

from sympy import Q
from sage_categories.all import Cat, Category, Fun, Sets, FiniteSets, Mor, ask, Unknown, pair_maps, parallel_pair
from sage_categories.cat.constructions import constructed_data
from sage_categories.cat.cones import cocone, cocones


def test_finite_set_universal_maps():
    X, Y = Sets((0, 1, 2)), Sets((0, 1))
    f = Mor(Sets)(X, Y)(lambda n: n % 2)
    factor, inclusion = Sets.image_factorization(f)
    assert ask(inclusion * factor == f) is True
    assert {point.datum() for point in factor.codomain()} == {0, 1}
    assert ask(f(X.point(0)) == f(X.point(2))) is True
    assert f(X.point(2)).parent() is Y
    assert X in FiniteSets
    assert FiniteSets is Sets().Finite()

    g = Mor(Sets)(X, Y)(lambda n: int(n > 0))
    pair = pair_maps(Sets, f, g)
    product = pair.codomain()
    assert ask(product.product_projection(0) * pair == f) is True
    assert ask(product.product_projection(1) * pair == g) is True
    assert pair(X.point(2)).datum() == (0, 1)
    assert pair(X.point(2)).parent() is product

    coproduct = Sets.Coproducts()((Y, Y))
    left, right = coproduct.coproduct_injection(0), coproduct.coproduct_injection(1)
    assert ask(left(Y.point(0)) == right(Y.point(0))) is False
    assert {point.datum() for point in coproduct} == {(0, 0), (0, 1), (1, 0), (1, 1)}

    source, target = Sets((0, 1)), Sets((0, 1, 2, 3))
    first = Mor(Sets)(source, target)(lambda n: n)
    second = Mor(Sets)(source, target)(lambda n: n + 1)
    diagram = parallel_pair(first, second)
    presentation = constructed_data(Sets.Colimits(diagram.domain()), diagram)
    q = presentation.leg(1)
    assert ask(q(target.point(0)) == q(target.point(2))) is True
    assert ask(q(target.point(0)) == q(target.point(3))) is False
    compatible = Mor(Sets)(target, Y)(lambda n: int(n == 3))
    candidate = cocone(diagram, Y, lambda v: compatible * first if diagram.domain().label(v) == 0 else compatible)
    desc = presentation.lift(cocones(diagram)(candidate))
    assert ask(desc * q == compatible) is True

    subobjects = Sets.Subobjects(X)
    subset = subobjects.from_predicate(lambda p: Q.even(p.datum()))
    mono = subobjects.defining_arrow().on_object(subset)
    assert {mono(p).datum() for p in mono.domain()} == {0, 2}


class PresentedSetsCategory(Category):
    class ObjectType:
        def __init__(self, data):
            self._enumeration = data
            self._carrier = Sets(data)

        def enumeration(self):
            return self._enumeration

    class ElementType:
        """Points inherited from the set projection."""

    class MorphismType:
        def __init__(self, arrow):
            self._set_map = arrow

    def __call__(self, enumeration):
        return self.ObjectType(enumeration)

    def to_sets(self):
        return Fun(self, Sets).Faithful().Isofibrations()(
            lambda value: value._carrier, lambda arrow: arrow._set_map)

    def structure_functors(self):
        return (self.to_sets(),)

    def construct_morphism(self, source, target, arrow):
        assert arrow.domain() is source._carrier and arrow.codomain() is target._carrier
        return self.MorphismType(domain=source, codomain=target, data=arrow)


def test_selected_set_functor_supplies_point_and_map_behavior():
    presented = PresentedSetsCategory()
    source, target = presented((0, 1, 2)), presented((0, 1))
    projection = presented.selected_functors()[0]
    X, Y = projection.on_object(source), projection.on_object(target)
    arrow = Mor(presented)(source, target)(Mor(Sets)(X, Y)(lambda n: n % 2))
    assert source.point(2).datum() == 2
    assert arrow(source.point(2)).datum() == 0
    assert projection.on_object(source) is X
    assert projection.on_morphism(arrow)(X.point(2)).parent() is Y


def test_rule_defined_infinite_set():
    integers = Sets.from_membership(lambda n: Q.integer(n))
    point = integers.point(7)
    constant = Sets.constant(integers, integers.point(2))
    assert ask(integers.membership_proposition(point)) is True
    assert constant(point).datum() == 2
    assert constant(point).parent() is integers
    assert (constant * constant)(point).datum() == 2
    assert Mor(Sets)(integers, integers).one()(point).datum() == 7
    assert ask(integers.is_finite()) is Unknown


test_finite_set_universal_maps()
test_rule_defined_infinite_set()
test_selected_set_functor_supplies_point_and_map_behavior()
