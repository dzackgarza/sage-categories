"""``FinitePosets()``: the structural diamond through finite sets, finiteness, and the finite order algorithms.

Oracles: both selected routes to ``Sets()`` return one retained value by identity
(``specs/resolution.md``, "Finite-rank free modules over finite fields"); the definitions
of bottom, top, cover, height (the size of a longest chain), width (the size of a
largest antichain), and a graded poset (ranked with all maximal chains of one length) on
the divisibility order of ``{1, 2, 3, 6}``, whose Hasse diagram is the square
``1 < 2, 3 < 6``; POL-CAT-062 for the category of every result.
"""

import pytest

from sage_categories.all import *


def _divisibility():
    carrier = Sets().Finite()((int(1), int(2), int(3), int(6)))
    return Posets()((carrier * carrier).subset_from(lambda pair: pair(int(1)) % pair(int(0)) == int(0)))


def _antichain():
    letters = Sets().Finite()(("a", "b"))
    return Posets()((letters * letters).subset_from(lambda pair: pair(int(0)) == pair(int(1))))


def test_the_structural_diamond_returns_one_underlying_set_map_and_point_by_identity() -> None:
    divisibility = _divisibility()
    inclusion, restricted = FinitePosets().structure_functors()
    underlying = Posets().structure_functors()[int(0)]
    finite_inclusion = Sets().Finite().structure_functors()[int(0)]
    carrier = underlying.on_object(divisibility)

    assert divisibility in FinitePosets()
    assert restricted in Fun(FinitePosets(), Sets().Finite())
    assert underlying.on_object(inclusion.on_object(divisibility)) is finite_inclusion.on_object(restricted.on_object(divisibility))
    assert restricted.on_object(divisibility) is carrier
    assert carrier in Sets().Finite()

    doubling = Mor(FinitePosets())(divisibility, divisibility)(lambda datum: datum if datum % int(2) == int(0) else int(2) * datum)
    assert doubling in Mor(FinitePosets())
    assert underlying.on_morphism(inclusion.on_morphism(doubling)) is finite_inclusion.on_morphism(restricted.on_morphism(doubling))
    assert restricted.on_morphism(doubling) in Mor(Sets().Finite())

    two = divisibility.element(carrier.point(int(2)))
    assert underlying.on_element(inclusion.on_element(two)) is finite_inclusion.on_element(restricted.on_element(two))
    assert restricted.on_element(two) is carrier.point(int(2))

    assert ask(divisibility.cardinality() == int(4)) is True
    assert len(list(divisibility)) == int(4)
    assert ask(doubling(two) == carrier.point(int(2))) is True


def test_finiteness_is_decided_from_the_underlying_set() -> None:
    usual = (ZZ * ZZ).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    integers = Posets()(usual)
    assert ask(integers.is_finite()) is False
    assert integers not in FinitePosets()

    words = Sets()(lambda datum: type(datum) is str)
    prefix = Posets()((words * words).subset_from(lambda pair: pair(int(1)).startswith(pair(int(0)))))
    assert ask(prefix.is_finite()) is Unknown
    assert ask(FinitePosets().predicate()(prefix)) is Unknown
    assume(prefix.is_finite())
    assert words in Sets().Finite()
    assert prefix not in FinitePosets()
    assert ask(FinitePosets().predicate()(prefix)) is True
    assert prefix in FinitePosets()


def test_the_finite_order_algorithms_reconstruct_owned_results() -> None:
    divisibility = _divisibility()
    carrier = Posets().structure_functors()[int(0)].on_object(divisibility)
    one, two, three, six = (divisibility.element(carrier.point(int(k))) for k in (1, 2, 3, 6))

    assert ask(divisibility.has_bottom()) is True
    assert divisibility in FinitePosets().WithBottom()
    assert divisibility.bottom() is one
    assert ask(divisibility.has_top()) is True
    assert divisibility.top() is six
    assert ask(divisibility.height() == int(3)) is True
    assert ask(divisibility.width() == int(2)) is True
    assert divisibility.covers(one, two) is True
    assert divisibility.covers(one, six) is False
    assert divisibility.covers(two, one) is False

    assert ask(divisibility.is_graded()) is True
    assert divisibility in FinitePosets().Graded()
    assert divisibility in FinitePosets().Ranked()
    assert ask(divisibility.rank() == int(2)) is True
    assert ask(divisibility.rank_of_element(one) == int(0)) is True
    assert ask(divisibility.rank_of_element(three) == int(1)) is True

    below_six = divisibility.lower_covers(six)
    assert below_six in FinitePosets()
    assert ask(below_six.cardinality() == int(2)) is True
    assert carrier.point(int(2)) in below_six
    assert carrier.point(int(3)) in below_six
    assert carrier.point(int(1)) not in below_six
    assert ask(below_six.element(below_six.point(int(2))) <= below_six.element(below_six.point(int(3)))) is False
    assert ask(divisibility.upper_covers(one).cardinality() == int(2)) is True
    assert ask(divisibility.minimal_elements().cardinality() == int(1)) is True
    assert carrier.point(int(6)) in divisibility.maximal_elements()


def test_bottom_and_top_belong_to_the_property_subcategories_that_guarantee_them() -> None:
    antichain = _antichain()
    assert ask(antichain.has_bottom()) is False
    assert antichain not in FinitePosets().WithBottom()
    assert ask(antichain.has_top()) is False
    with pytest.raises(AttributeError):
        antichain.bottom
    with pytest.raises(AttributeError):
        antichain.top
    assert ask(antichain.height() == int(1)) is True
    assert ask(antichain.width() == int(2)) is True
    assert ask(antichain.is_ranked()) is True
    assert ask(antichain.rank() == int(0)) is True
