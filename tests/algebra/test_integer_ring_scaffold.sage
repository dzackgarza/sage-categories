"""The integers as a rule-defined carrier: a group and a ring whose laws are decided symbolically, without enumeration."""

from sympy import Lambda, Q, symbols

from sage_categories.all import Mor, Sets, Cartesian, ask, Unknown
from sage_categories.cat.structured_objects import AdditiveGroups, Groups, Monoids, Rings
from sage_categories.cat.calculus import binary_product_data


def integer_operations():
    integers = Sets.from_membership(lambda n: Q.integer(n))
    structure = Cartesian(Sets())
    square = binary_product_data(Sets(), integers, integers).apex()
    a, b = symbols("a b")
    addition = Mor(Sets)(square, integers)(Lambda((a, b), a + b))
    product(x, y) = x * y
    multiplication = Mor(Sets)(square, integers)(product)
    zero = Mor(Sets)(structure.unit(), integers)(lambda _: 0)
    one = Mor(Sets)(structure.unit(), integers)(lambda _: 1)
    return integers, structure, addition, zero, multiplication, one


def test_integers_form_a_group_with_symbolic_inversion() -> None:
    integers, structure, addition, zero, _, _ = integer_operations()
    monoid = Monoids(structure)(addition, zero)
    assert ask(monoid.is_group()) is True
    assert monoid in Groups(structure).Commutative()
    inversion = monoid.inversion()
    assert inversion(integers.point(5)).datum() == -5
    assert inversion(integers.point(-12)).datum() == 12
    group = AdditiveGroups(structure).renamed(monoid)
    assert (-group.point(7)).datum() == -7
    assert (group.point(3) - group.point(10)).datum() == -7
    assert group.zero().datum() == 0


def test_integers_form_a_commutative_ring() -> None:
    integers, _, addition, zero, multiplication, one = integer_operations()
    rings = Rings(Sets())
    ring = rings(addition, zero, multiplication, one)
    assert ring in rings.Commutative()
    assert ring.one().datum() == 1
    assert ((-ring.point(2)) * ring.point(3)).datum() == -6
    assert ((ring.point(2) + ring.point(5)) * ring.point(4)).datum() == 28
    assert ask(ring.point(6) * ring.point(7) == ring.point(42)) is True


def test_doubling_is_monic_and_not_epic() -> None:
    integers, _, _, _, _, _ = integer_operations()
    a = symbols("a")
    doubling = Mor(Sets)(integers, integers)(Lambda(a, 2 * a))
    assert doubling(integers.point(21)).datum() == 42
    assert ask(Mor(Sets).Monomorphisms().membership_proposition(doubling)) is True
    assert ask(Mor(Sets).Epimorphisms().membership_proposition(doubling)) is False
    negation = Mor(Sets)(integers, integers)(Lambda(a, -a))
    assert ask(Mor(Sets).Isomorphisms().membership_proposition(negation)) is True
    assert negation.inverse()(integers.point(4)).datum() == -4
    # Two rules that agree everywhere are one map; two that differ at a point are not; opaque rules stay undecided.
    assert ask(Mor(Sets)(integers, integers)(Lambda(a, (a + 1) ** 2 - 2 * a - 1)) == Mor(Sets)(integers, integers)(Lambda(a, a**2))) is True
    assert ask(doubling == negation) is False
    assert ask(Mor(Sets)(integers, integers)(lambda n: n) == Mor(Sets)(integers, integers)(lambda n: abs(n) * (1 if n >= 0 else -1))) is Unknown


test_integers_form_a_group_with_symbolic_inversion()
test_integers_form_a_commutative_ring()
test_doubling_is_monic_and_not_epic()
