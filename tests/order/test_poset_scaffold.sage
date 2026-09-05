"""Sets with a binary relation, partial orders, total orders, and monotone maps."""

from sympy import true, false

from sage_categories.all import Cat, Fun, Mor, Sets, ask
from sage_categories.order.posets import BinaryRelations, Posets, TotallyOrderedSets


def _chain_relation(size):
    carrier = Sets(tuple(range(size)))
    relation = BinaryRelations().from_predicate(
        carrier, lambda a, b: true if a.datum() <= b.datum() else false
    )
    return relation.relation()


def test_partial_order_admission_and_counterexample() -> None:
    carrier = Sets((0, 1))
    equality = BinaryRelations().from_predicate(carrier, lambda a, b: a == b)
    assert equality in BinaryRelations()
    assert ask(equality.is_partial_order()) is True
    assert ask(Posets().membership_proposition(equality)) is True

    crossed = BinaryRelations().from_predicate(
        carrier, lambda a, b: true if a.datum() != b.datum() else false
    )
    assert ask(crossed.is_partial_order()) is False
    assert ask(Posets().membership_proposition(crossed)) is False


def test_order_comparison_on_owned_points() -> None:
    equality = Posets()(BinaryRelations().from_predicate(Sets((0, 1)), lambda a, b: a == b).relation())
    low, high = equality.point(0), equality.point(1)
    assert low.parent() is equality
    assert ask(low <= low) is True
    assert ask(low <= high) is False
    assert ask(high <= low) is False


def test_total_order_refines_a_poset() -> None:
    chain = Posets()(_chain_relation(3))
    assert chain in Posets()
    assert ask(chain.is_total()) is True
    assert ask(TotallyOrderedSets().membership_proposition(chain)) is True
    bottom, middle, top = chain.point(0), chain.point(1), chain.point(2)
    assert ask(bottom <= top) is True
    assert ask(top <= bottom) is False

    equality = Posets()(BinaryRelations().from_predicate(Sets((0, 1)), lambda a, b: a == b).relation())
    assert ask(equality.is_total()) is False
    assert ask(TotallyOrderedSets().membership_proposition(equality)) is False


def test_monotone_maps_and_reversing_rejection() -> None:
    source = Posets()(_chain_relation(3))
    target = Posets()(_chain_relation(2))
    underlying = Mor(Sets)(source.carrier(), target.carrier())(lambda n: min(n, 1))
    monotone = Mor(Posets())(source, target)(underlying)
    image = monotone(source.point(2))
    assert image.parent() is target
    assert image.datum() == 1
    assert monotone(source.point(0)).datum() == 0

    reversing = Mor(Sets)(target.carrier(), target.carrier())(lambda n: 1 - n)
    try:
        Mor(Posets())(target, target)(reversing)
        raise AssertionError("a reversing map must fail monotone admission")
    except AssertionError as error:
        assert "does not preserve" in str(error)


test_partial_order_admission_and_counterexample()
test_order_comparison_on_owned_points()
test_total_order_refines_a_poset()
test_monotone_maps_and_reversing_rejection()
