"""``FinitePosets()``: the structural diamond through finite sets, finiteness, and the finite order algorithms.

Oracles: both selected routes to ``Sets()`` return one retained value by identity
(``specs/resolution.md``, "Finite-rank free modules over finite fields"); the definitions
of bottom, top, cover, height (the size of a longest chain), width (the size of a
largest antichain), and a graded poset (ranked with all maximal chains of one length) on
the divisibility order of ``{1, 2, 3, 6}``, whose Hasse diagram is the square
``1 < 2, 3 < 6``; the definitions of open and closed intervals, principal ideals and
filters, the down- and up-closures of a subset, chains, and antichains; Szpilrajn's
extension theorem (every partial order on a set extends to a linear order on that set)
for the linear extension; the rank levels ``{1}, {2, 3}, {6}`` of the graded
divisibility order; POL-CAT-062 for the category of every result.
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
    monomorphism, restricted = FinitePosets().structure_functors()
    underlying = Posets().structure_functors()[int(0)]
    into_sets = Sets().Finite().structure_functors()[int(0)]
    carrier = underlying.on_object(divisibility)

    assert divisibility in FinitePosets()
    assert restricted in Fun(FinitePosets(), Sets().Finite())
    assert underlying.on_object(monomorphism.on_object(divisibility)) is into_sets.on_object(restricted.on_object(divisibility))
    assert restricted.on_object(divisibility) is carrier
    assert carrier in Sets().Finite()

    doubling = Mor(FinitePosets())(divisibility, divisibility)(lambda datum: datum if datum % int(2) == int(0) else int(2) * datum)
    assert doubling in Mor(FinitePosets())
    assert underlying.on_morphism(monomorphism.on_morphism(doubling)) is into_sets.on_morphism(restricted.on_morphism(doubling))
    assert restricted.on_morphism(doubling) in Mor(Sets().Finite())

    two = divisibility.element(carrier.point(int(2)))
    assert underlying.on_element(monomorphism.on_element(two)) is into_sets.on_element(restricted.on_element(two))
    assert restricted.on_element(two) is carrier.point(int(2))

    assert ask(divisibility.cardinality() == int(4))
    assert len(list(divisibility)) == int(4)
    assert ask(doubling(two) == carrier.point(int(2)))


def test_finiteness_is_decided_from_the_underlying_set() -> None:
    usual = (ZZ * ZZ).subset_from(lambda pair: pair(int(0)) <= pair(int(1)))
    integers = Posets()(usual)
    assert not ask(integers.is_finite())
    assert integers not in FinitePosets()

    letters = Sets()(lambda datum: datum in ("a", "ab"))
    prefix = Posets()((letters * letters).subset_from(lambda pair: pair(int(1)).startswith(pair(int(0)))))
    assert ask(prefix.is_finite()) is not True
    assert ask(FinitePosets().predicate()(prefix)) is not True
    assume(prefix.is_finite())
    assert letters in Sets().Finite()
    assert prefix not in FinitePosets()
    assert ask(FinitePosets().predicate()(prefix))
    assert prefix in FinitePosets()


def test_the_finite_order_algorithms_reconstruct_owned_results() -> None:
    divisibility = _divisibility()
    carrier = Posets().structure_functors()[int(0)].on_object(divisibility)
    one, two, three, six = (divisibility.element(carrier.point(int(k))) for k in (1, 2, 3, 6))

    assert ask(divisibility.has_bottom())
    assert divisibility in FinitePosets().WithBottom()
    assert divisibility.bottom() is one
    assert ask(divisibility.has_top())
    assert divisibility.top() is six
    assert ask(divisibility.height() == int(3))
    assert ask(divisibility.width() == int(2))
    assert divisibility.covers(one, two)
    assert not divisibility.covers(one, six)
    assert not divisibility.covers(two, one)

    assert ask(divisibility.is_graded())
    assert divisibility in FinitePosets().Graded()
    assert divisibility in FinitePosets().Ranked()
    assert ask(divisibility.rank() == int(2))
    assert ask(divisibility.rank_of_element(one) == int(0))
    assert ask(divisibility.rank_of_element(three) == int(1))

    below_six = divisibility.lower_covers(six)
    assert below_six in FinitePosets()
    assert ask(below_six.cardinality() == int(2))
    assert carrier.point(int(2)) in below_six
    assert carrier.point(int(3)) in below_six
    assert carrier.point(int(1)) not in below_six
    assert not ask(below_six.element(below_six.point(int(2))) <= below_six.element(below_six.point(int(3))))
    assert ask(divisibility.upper_covers(one).cardinality() == int(2))
    assert ask(divisibility.minimal_elements().cardinality() == int(1))
    assert carrier.point(int(6)) in divisibility.maximal_elements()


def test_bottom_and_top_belong_to_the_property_subcategories_that_guarantee_them() -> None:
    antichain = _antichain()
    assert not ask(antichain.has_bottom())
    assert antichain not in FinitePosets().WithBottom()
    assert not ask(antichain.has_top())
    with pytest.raises(AttributeError):
        antichain.bottom
    with pytest.raises(AttributeError):
        antichain.top
    assert ask(antichain.height() == int(1))
    assert ask(antichain.width() == int(2))
    assert ask(antichain.is_ranked())
    assert ask(antichain.rank() == int(0))


def test_intervals_ideals_filters_and_common_covers_are_sub_posets() -> None:
    divisibility = _divisibility()
    carrier = Posets().structure_functors()[int(0)].on_object(divisibility)
    one, two, six = (divisibility.element(carrier.point(int(k))) for k in (1, 2, 6))
    middle = divisibility.sub_poset(lambda datum: datum in (int(2), int(3)))

    closed = divisibility.closed_interval(one, six)
    assert closed in FinitePosets()
    assert ask(closed.cardinality() == int(4))
    between = divisibility.open_interval(one, six)
    assert ask(between.cardinality() == int(2))
    assert carrier.point(int(2)) in between
    assert carrier.point(int(3)) in between
    assert not ask(between.element(between.point(int(2))) <= between.element(between.point(int(3))))
    assert divisibility.is_antichain_of_poset(between)
    assert not divisibility.is_chain_of_poset(between)
    assert divisibility.is_chain_of_poset(divisibility.sub_poset(lambda datum: datum != int(3)))

    below_two = divisibility.principal_order_ideal(two)
    assert ask(below_two.cardinality() == int(2))
    assert carrier.point(int(1)) in below_two
    assert carrier.point(int(2)) in below_two
    above_two = divisibility.principal_order_filter(two)
    assert ask(above_two.cardinality() == int(2))
    assert carrier.point(int(6)) in above_two
    assert ask(divisibility.order_ideal(middle).cardinality() == int(3))
    assert carrier.point(int(6)) not in divisibility.order_ideal(middle)
    assert ask(divisibility.order_filter(middle).cardinality() == int(3))
    assert carrier.point(int(1)) not in divisibility.order_filter(middle)
    assert ask(divisibility.common_lower_covers(middle).cardinality() == int(1))
    assert carrier.point(int(1)) in divisibility.common_lower_covers(middle)
    assert carrier.point(int(6)) in divisibility.common_upper_covers(middle)


def test_a_linear_extension_is_a_finite_total_order_on_the_same_set_extending_the_order() -> None:
    divisibility = _divisibility()
    underlying = Posets().structure_functors()[int(0)]
    carrier = underlying.on_object(divisibility)
    extension = divisibility.linear_extension()

    assert extension in TotallyOrderedSets()
    assert extension in FiniteTotallyOrderedSets()
    assert underlying.on_object(extension) is carrier
    assert ask(extension.cardinality() == int(4))
    for lower, upper in ((1, 2), (1, 3), (2, 6), (3, 6)):
        assert ask(divisibility.element(carrier.point(int(lower))) <= divisibility.element(carrier.point(int(upper))))
        assert ask(extension.element(carrier.point(int(lower))) <= extension.element(carrier.point(int(upper))))

    chain = Posets().Simplex(int(2))
    assert FiniteTotallyOrderedSets() is FinitePosets().TotallyOrdered()
    assert chain in FiniteTotallyOrderedSets()
    assert ask(chain.cardinality() == int(3))


def test_level_sets_of_a_ranked_poset_are_its_rank_levels_indexed_by_a_discrete_diagram() -> None:
    divisibility = _divisibility()
    carrier = Posets().structure_functors()[int(0)].on_object(divisibility)
    assert ask(divisibility.is_ranked())
    levels = divisibility.level_sets()
    index = Sets().Simplex(int(2))

    assert levels in Fun(Discrete(index), Posets())
    level = tuple(levels.on_object(Discrete(index)(index.point(int(k)))) for k in range(3))
    assert all(member in FinitePosets() for member in level)
    assert [ask(member.cardinality() == int(size)) for member, size in zip(level, (1, 2, 1))] == [True, True, True]
    assert carrier.point(int(1)) in level[int(0)]
    assert carrier.point(int(2)) in level[int(1)]
    assert carrier.point(int(3)) in level[int(1)]
    assert carrier.point(int(6)) in level[int(2)]
    for member, rank in ((1, 0), (2, 1), (3, 1), (6, 2)):
        assert ask(divisibility.rank_of_element(divisibility.element(carrier.point(int(member)))) == int(rank))
