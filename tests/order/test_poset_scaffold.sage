"""Sets with a binary relation, partial orders, total orders, and monotone maps."""

import pytest
from sympy import true, false

from sage_categories.all import Cat, Mor, Sets, ask
from sage_categories.cat.cones import cone
from sage_categories.order.posets import BinaryRelations, Posets, Thin, TotallyOrderedSets


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
    with pytest.raises(AssertionError):
        Mor(Posets())(target, target)(reversing)


def test_product_of_two_chains_carries_the_componentwise_order() -> None:
    """``Posets().Products()`` lifts the selected set product along the faithful projection (D183)."""
    first_factor = Posets()(_chain_relation(2))
    second_factor = Posets()(_chain_relation(2))
    product = Posets().Products()(first_factor, second_factor)
    assert product in Posets()

    projection = BinaryRelations().to_sets()
    image_diagram = projection * product.product_factors()
    selected = Sets.Limits(image_diagram.domain()).universal_data(image_diagram)
    assert product.carrier() is selected.apex()
    assert projection.on_object(product) is selected.apex()

    # ``(0, 1)`` and ``(1, 0)`` disagree in both coordinates, so neither compares.
    left, right = product.point((0, 1)), product.point((1, 0))
    assert ask(left <= right) is False
    assert ask(right <= left) is False
    assert ask(product.point((0, 0)) <= product.point((1, 1))) is True
    assert ask(left <= left) is True
    # The crossed points are incomparable, so the product of two chains is not total.
    assert ask(product.is_total()) is False
    assert ask(TotallyOrderedSets().membership_proposition(product)) is False

    for index, factor in enumerate((first_factor, second_factor)):
        leg = product.product_projection(index)
        assert leg.domain() is product and leg.codomain() is factor
        assert projection.on_morphism(leg) is selected.leg(index)
    assert product.product_projection(0)(left).datum() == 0
    assert product.product_projection(1)(left).datum() == 1


def test_competing_cone_over_the_product_has_the_monotone_mediator() -> None:
    """The universal property of the lifted product, against a cone whose legs differ."""
    two, three = Posets()(_chain_relation(2)), Posets()(_chain_relation(3))
    product = Posets().Products()(two, two)
    lower = Mor(Posets())(three, two)(Mor(Sets)(three.carrier(), two.carrier())(lambda n: min(n, 1)))
    upper = Mor(Posets())(three, two)(Mor(Sets)(three.carrier(), two.carrier())(lambda n: int(n >= 2)))

    factors = product.product_factors()
    shape = factors.domain()
    candidate = cone(factors, three, lambda vertex: (lower, upper)[shape.label(vertex)])
    mediator = product.universal_morphism(candidate)
    assert mediator.domain() is three and mediator.codomain() is product
    assert mediator(three.point(0)).datum() == (0, 0)
    assert mediator(three.point(1)).datum() == (1, 0)
    assert mediator(three.point(2)).datum() == (1, 1)
    for index, leg in enumerate((lower, upper)):
        assert ask(product.product_projection(index) * mediator == leg) is True


def test_transport_along_a_bijection_lifts_it_to_an_isomorphism() -> None:
    """The isofibration lift: a bijection of carriers carries the order to its image (D183)."""
    chain = Posets()(_chain_relation(3))
    cycle = {0: 2, 1: 0, 2: 1}
    bijection = Mor(Sets)(chain.carrier(), chain.carrier())(lambda n: cycle[n])
    isomorphism = BinaryRelations().transport(chain, bijection)
    moved = isomorphism.codomain()

    assert ask(Posets().membership_proposition(moved)) is True
    assert isomorphism.underlying_map() is bijection
    assert isomorphism in Mor(Posets())(chain, moved)
    assert isomorphism(chain.point(0)).datum() == 2

    # The transported order is ``2 <= 0 <= 1``: the image of ``0 <= 1 <= 2`` under the cycle.
    assert ask(moved.point(2) <= moved.point(0)) is True
    assert ask(moved.point(0) <= moved.point(1)) is True
    assert ask(moved.point(0) <= moved.point(2)) is False
    assert ask(moved.point(1) <= moved.point(0)) is False
    # The two orders share one carrier and stay distinct.
    assert ask(chain.point(0) <= chain.point(2)) is True

    assert len(moved) == 3
    assert sorted(point.datum() for point in moved) == [0, 1, 2]
    assert moved.point(1) in moved


def test_transport_carries_an_incomparable_pair_to_a_new_carrier() -> None:
    """Transport onto a different set: the inherited set behaviour is that of the image."""
    two = Posets()(_chain_relation(2))
    product = Posets().Products()(two, two)
    letters = Sets(("bottom", "left", "right", "top"))
    naming = {(0, 0): "bottom", (0, 1): "left", (1, 0): "right", (1, 1): "top"}
    bijection = Mor(Sets)(product.carrier(), letters)(lambda pair: naming[pair])
    moved = BinaryRelations().transport(product, bijection).codomain()

    assert ask(Posets().membership_proposition(moved)) is True
    assert ask(moved.point("left") <= moved.point("right")) is False
    assert ask(moved.point("right") <= moved.point("left")) is False
    assert ask(moved.point("bottom") <= moved.point("top")) is True

    assert len(moved) == 4
    assert sorted(point.datum() for point in moved) == ["bottom", "left", "right", "top"]
    assert moved.point("top") in moved


def test_thin_sends_a_poset_to_its_thin_category() -> None:
    """``Thin: Posets() -> Cat()``: objects are points, one arrow per established comparison."""
    chain = Posets()(_chain_relation(3))
    thin = Thin.on_object(chain)
    assert thin in Cat()
    assert Thin.on_object(chain) is thin

    bottom, middle, top = (thin(chain.point(value)) for value in (0, 1, 2))
    assert thin(chain.point(0)) is bottom
    arrow = Mor(thin)(bottom, top)()
    assert arrow.domain() is bottom and arrow.codomain() is top
    composite = Mor(thin)(middle, top)() * Mor(thin)(bottom, middle)()
    assert composite.domain() is bottom and composite.codomain() is top

    antichain = Posets()(
        BinaryRelations().from_predicate(Sets((0, 1)), lambda a, b: a == b).relation()
    )
    discrete = Thin.on_object(antichain)
    with pytest.raises(AssertionError):
        Mor(discrete)(discrete(antichain.point(0)), discrete(antichain.point(1)))()


def test_thin_sends_a_monotone_map_to_a_functor_of_thin_categories() -> None:
    """The morphism action: a point to its image and a comparison to the compared images."""
    three, two = Posets()(_chain_relation(3)), Posets()(_chain_relation(2))
    monotone = Mor(Posets())(three, two)(
        Mor(Sets)(three.carrier(), two.carrier())(lambda n: min(n, 1))
    )
    induced = Thin.on_morphism(monotone)
    source, target = Thin.on_object(three), Thin.on_object(two)
    assert induced.domain() is source and induced.codomain() is target

    bottom, top = source(three.point(0)), source(three.point(2))
    image = induced.on_morphism(Mor(source)(bottom, top)())
    assert image.domain() is target(two.point(0))
    assert image.codomain() is target(two.point(1))
    assert induced.on_object(top) is target(two.point(1))


test_partial_order_admission_and_counterexample()
test_order_comparison_on_owned_points()
test_total_order_refines_a_poset()
test_monotone_maps_and_reversing_rejection()
test_product_of_two_chains_carries_the_componentwise_order()
test_competing_cone_over_the_product_has_the_monotone_mediator()
test_transport_along_a_bijection_lifts_it_to_an_isomorphism()
test_transport_carries_an_incomparable_pair_to_a_new_carrier()
test_thin_sends_a_poset_to_its_thin_category()
test_thin_sends_a_monotone_map_to_a_functor_of_thin_categories()
