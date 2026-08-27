"""``Posets()``: partial orders as chosen relations, monotone maps, the underlying-set functor, and inherited results.

Oracles: the definition of a partial order (reflexive, antisymmetric, transitive) and of
a total order; the definition of the induced order on a subset, the ``U``-initial lift
of its inclusion (Adamek, Herrlich, Strecker, Definition 10.41 and Example 10.42(6);
Mathlib ``PartialOrder.lift``); POL-CAT-062 for the category of every inherited result
(the declaring method's value in ``Sets()``); ``specs/functor.md`` for the classical
stage, its identity comparison under ``U``, and the generalized elements at other
stages; the usual order on ``{0, 1, 2}`` and divisibility on ``{1, 2, 3, 6}``.
"""

import pytest

from sage_categories.all import *


def _divisibility():
    """The divisibility order on ``{1, 2, 3, 6}``: ``a <= b`` when ``a`` divides ``b``."""
    carrier = Sets().Finite()((int(1), int(2), int(3), int(6)))
    return Posets()((carrier * carrier).subset_from(lambda pair: pair(int(1)) % pair(int(0)) == int(0)))


def _underlying():
    return Posets().structure_functors()[int(0)]


def test_a_poset_is_constructed_from_its_relation_and_compares_its_elements() -> None:
    divisibility = _divisibility()
    carrier = _underlying().on_object(divisibility)
    one, two, three, six = (divisibility.element(carrier.point(int(k))) for k in (1, 2, 3, 6))

    assert divisibility in Posets()
    assert divisibility in FinitePosets()
    assert divisibility.relation() in Sets().ChosenSubsets()
    assert divisibility.relation().underlying_set() is carrier * carrier
    assert ask(two <= six) is True
    assert ask(two <= three) is False
    assert ask(three <= six) is True
    assert ask(six <= two) is False
    assert ask(two <= two) is True
    assert ask(two < two) is False
    assert ask(one < six) is True
    assert ask(six >= two) is True
    assert ask(two > one) is True
    assert ask(two == two) is True
    assert ask(two == divisibility.element(carrier.point(int(2)))) is True
    assert ask(two == three) is False
    assert ask(divisibility.is_total()) is False
    assert divisibility not in TotallyOrderedSets()


def test_a_relation_that_is_not_a_partial_order_is_rejected_and_an_infinite_one_is_trusted() -> None:
    three = Sets().Simplex(int(2))
    covers = {(int(0), int(0)), (int(1), int(1)), (int(2), int(2)), (int(0), int(1)), (int(1), int(2))}
    not_transitive = (three * three).subset_from(lambda pair: (pair(int(0)), pair(int(1))) in covers)
    assert ask(Posets().is_partial_order(not_transitive)) is False
    with pytest.raises(AssertionError):
        Posets()(not_transitive)

    strict = (three * three).subset_from(lambda pair: pair(int(0)) < pair(int(1)))
    assert ask(Posets().is_partial_order(strict)) is False

    two = Sets().Simplex(int(1))
    mixed = (two * three).subset_from(lambda pair: True)
    with pytest.raises(AssertionError):
        Posets()(mixed)

    usual = (ZZ * ZZ).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    assert ask(Posets().is_partial_order(usual)) is not False
    integers = Posets()(usual)
    assert integers in Posets()
    assert integers not in FinitePosets()
    assert ask(integers.is_finite()) is False
    assert ask(integers.element(ZZ(int(3))) <= integers.element(ZZ(int(5)))) is True
    assert ask(integers.element(ZZ(int(5))) <= integers.element(ZZ(int(3)))) is False
    assert ask(integers.is_total()) is not False


def test_totality_is_decided_on_finite_carriers_and_the_simplex_has_the_usual_order() -> None:
    chain = Posets().Simplex(int(2))
    carrier = Sets().Simplex(int(2))
    zero, one, two = (chain.element(carrier.point(int(k))) for k in range(3))

    assert chain in TotallyOrderedSets()
    assert chain in FinitePosets()
    assert _underlying().on_object(chain) is carrier
    assert ask(zero <= one) is True
    assert ask(one <= zero) is False
    assert ask(zero < two) is True
    assert ask(two <= two) is True

    letters = Sets().Finite()(("a", "b"))
    ordered = Posets()((letters * letters).subset_from(lambda pair: pair(int(0)) <= pair(int(1))))
    assert ordered not in TotallyOrderedSets()
    assert ask(ordered.is_total()) is True
    assert ordered in TotallyOrderedSets()

    equality = Posets()((letters * letters).subset_from(lambda pair: pair(int(0)) == pair(int(1))))
    assert ask(equality.is_total()) is False
    assert equality not in TotallyOrderedSets()


def test_monotone_maps_are_constructed_from_rules_and_inherit_the_set_map_surface() -> None:
    chain, pair = Posets().Simplex(int(2)), Posets().Simplex(int(1))
    three, two = Sets().Simplex(int(2)), Sets().Simplex(int(1))
    collapse = Mor(Posets())(chain, pair)(lambda datum: min(datum, int(1)))
    include = Mor(Posets())(pair, chain)(lambda datum: datum)

    assert collapse in Mor(Posets())(chain, pair)
    assert collapse in Mor(Posets())
    assert _underlying().on_morphism(collapse) in Mor(Sets())(three, two)
    top = chain.element(three.point(int(2)))
    assert ask(collapse(top) == two.point(int(1))) is True
    assert collapse(top).parent() is two
    assert ask(collapse * include == pair.identity()) is True
    assert ask(include * collapse == chain.identity()) is False
    assert chain.identity() in Mor(Posets()).Automorphisms()
    assert chain.identity().inverse() is chain.identity()

    with pytest.raises(AssertionError):
        Mor(Posets())(chain, chain)(lambda datum: int(2) - datum)
    assert ask(Posets().is_order_preserving(chain, chain, Mor(Sets())(three, three)(lambda datum: int(2) - datum))) is False
    assert ask(Posets().is_order_preserving(chain, chain, Mor(Sets())(three, three)(lambda datum: int(0)))) is True


def test_inherited_results_are_the_declaring_methods_values_in_sets() -> None:
    divisibility = _divisibility()
    carrier = _underlying().on_object(divisibility)

    cardinality = divisibility.cardinality()
    assert cardinality is carrier.cardinality()
    assert cardinality in Cardinal()
    assert ask(cardinality == int(4)) is True
    assert ask(divisibility.is_countable()) is True

    point = divisibility.point(int(6))
    assert point is carrier.point(int(6))
    assert point.parent() is carrier
    assert point in divisibility
    assert divisibility.element(point) in divisibility

    evens = divisibility.subset_from(lambda datum: datum % int(2) == int(0))
    assert evens in Sets()
    assert evens not in Posets()
    assert evens.underlying_set() is carrier
    assert evens.inclusion() in Mor(Sets())(evens, carrier)
    assert ask(evens.cardinality() == int(2)) is True

    points = list(divisibility)
    assert len(points) == int(4)
    assert all(point.parent() is carrier for point in points)

    with pytest.raises(AttributeError):
        Sets().ObjectType.sub_poset
    with pytest.raises(AttributeError):
        evens.sub_poset


def test_the_leaf_override_sub_poset_returns_the_induced_order_through_the_retained_lift() -> None:
    divisibility = _divisibility()
    carrier = _underlying().on_object(divisibility)
    without_three = divisibility.sub_poset(lambda datum: datum != int(3))
    subset = divisibility.subset_from(lambda datum: datum != int(3))
    lift = _underlying().cartesian_lift(subset.inclusion(), divisibility)

    assert without_three in Posets()
    assert without_three in FinitePosets()
    assert ask(without_three.cardinality() == int(3)) is True
    one, two, six = (without_three.element(without_three.point(int(k))) for k in (1, 2, 6))
    assert ask(one <= two) is True
    assert ask(two <= six) is True
    assert ask(six <= two) is False
    assert ask(one <= six) is True

    assert lift in Mor(Posets())
    assert lift.codomain() is divisibility
    assert _underlying().on_morphism(lift) is subset.inclusion()
    assert _underlying().on_object(lift.domain()) is subset
    assert ask(lift(two) == carrier.point(int(2))) is True

    collapse = Mor(Sets())(carrier, carrier)(lambda datum: int(1))
    with pytest.raises(AssertionError):
        _underlying().cartesian_lift(collapse, divisibility)


def test_the_classical_stage_is_the_one_point_order_with_the_identity_comparison() -> None:
    divisibility = _divisibility()
    carrier = _underlying().on_object(divisibility)
    one_point = Posets().Terminal()

    assert Posets().classical_stages() == (one_point,)
    assert _underlying().on_object(one_point) is Sets().Terminal()
    assert _underlying().stage_comparison() is Sets().Terminal().identity()

    two = divisibility.element(carrier.point(int(2)))
    assert two.stage() is one_point
    assert two.parent() is divisibility
    assert two.defining_morphism() in Mor(Posets())(one_point, divisibility)
    assert _underlying().on_element(two) is carrier.point(int(2))
    assert Posets().element_from_defining_morphism(two.defining_morphism()) is two
    assert hash(two) == hash(carrier.point(int(2)))

    pair = Posets().Simplex(int(1))
    comparable = Mor(Posets())(pair, divisibility)(lambda datum: int(2) if datum == int(0) else int(6))
    generalized = Posets().element_from_defining_morphism(comparable)
    assert generalized.stage() is pair
    assert generalized.parent() is divisibility
    assert generalized.defining_morphism() is comparable


def test_the_thin_category_of_a_poset_has_one_comparison_per_related_pair() -> None:
    divisibility = _divisibility()
    carrier = _underlying().on_object(divisibility)
    thin = divisibility.thin_category()
    two, three, six = (thin(carrier.point(int(k))) for k in (2, 3, 6))

    assert thin is divisibility.thin_category()
    assert thin in Cat()
    assert thin.carrier() is carrier
    assert Mor(thin)(two, six)() in Mor(thin)(two, six)
    assert ask(Mor(thin)(six, six)() == six.identity()) is True
    with pytest.raises(AssertionError):
        Mor(thin)(two, three)()
    assert Posets().Simplex(int(2)).thin_category() is not Cat().Simplex(int(2))
