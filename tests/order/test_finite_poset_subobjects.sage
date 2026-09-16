"""Owned induced subposets and finite collection-valued order constructions."""

from sympy import Q, false, true

from sage_categories.all import FinitePosets, Posets, Sets, ask
from sage_categories.order.posets import BinaryRelations


def _divisibility():
    carrier = Sets((1, 2, 3, 6))
    relation = BinaryRelations().from_predicate(
        carrier,
        lambda first, second: true if second.datum() % first.datum() == 0 else false,
    )
    return FinitePosets()(relation.relation())


def _selected_data(ambient, subobject):
    subobjects = Posets().Subobjects(ambient)
    assert subobject in subobjects
    assert subobject in subobjects.Finite()
    inclusion = subobjects.defining_arrow().on_object(subobject)
    assert inclusion.codomain() is ambient
    underlying = Posets().to_sets().on_morphism(inclusion)
    assert underlying.codomain() is ambient.carrier()
    induced = inclusion.domain()
    assert induced in Posets()
    assert induced in FinitePosets()
    return {inclusion(point).datum() for point in induced}


def test_induced_subposet_retains_the_exact_poset_and_carrier_inclusions() -> None:
    ambient = _divisibility()
    subobjects = Posets().Subobjects(ambient)
    selected = subobjects.from_predicate(
        lambda point: true if point.datum() in (2, 3) else false
    )
    inclusion = subobjects.defining_arrow().on_object(selected)
    induced = inclusion.domain()

    assert inclusion.codomain() is ambient
    assert inclusion in Posets().morphism_category(1).Monomorphisms()
    assert _selected_data(ambient, selected) == {2, 3}
    two, three = induced.point(2), induced.point(3)
    assert ask(two <= three) is False
    assert ask(three <= two) is False
    assert inclusion(two) is ambient.point(2)
    assert inclusion(three) is ambient.point(3)


def test_induced_subposet_constructor_does_not_require_a_finite_ambient() -> None:
    integers = Sets.from_membership(Q.integer)
    relation = BinaryRelations().from_predicate(
        integers,
        lambda first, second: Q.nonnegative(second.datum() - first.datum()),
    )
    ambient = Posets()(relation.relation())
    subobjects = Posets().Subobjects(ambient)
    evens = subobjects.from_predicate(lambda point: Q.even(point.datum()))
    inclusion = subobjects.defining_arrow().on_object(evens)
    induced = inclusion.domain()

    assert inclusion.codomain() is ambient
    assert Posets().to_sets().on_morphism(inclusion).codomain() is integers
    assert ask(induced.point(2) <= induced.point(4)) is True
    assert ask(induced.point(4) <= induced.point(2)) is False


def test_finite_collection_algorithms_return_owned_subobjects() -> None:
    ambient = _divisibility()
    one, two, three, six = (ambient.point(value) for value in (1, 2, 3, 6))
    subobjects = Posets().Subobjects(ambient)
    middle = subobjects.from_predicate(
        lambda point: true if point.datum() in (2, 3) else false
    )

    expected = (
        (ambient.lower_covers(six), {2, 3}),
        (ambient.upper_covers(one), {2, 3}),
        (ambient.open_interval(one, six), {2, 3}),
        (ambient.closed_interval(one, six), {1, 2, 3, 6}),
        (ambient.principal_order_ideal(two), {1, 2}),
        (ambient.principal_order_filter(two), {2, 6}),
        (ambient.order_ideal(middle), {1, 2, 3}),
        (ambient.order_filter(middle), {2, 3, 6}),
        (ambient.common_lower_covers(middle), {1}),
        (ambient.common_upper_covers(middle), {6}),
        (ambient.minimal_elements(), {1}),
        (ambient.maximal_elements(), {6}),
    )
    for subobject, data in expected:
        assert _selected_data(ambient, subobject) == data

    chain = subobjects.from_predicate(
        lambda point: true if point.datum() in (1, 2, 6) else false
    )
    assert ask(ambient.is_chain_of_poset(chain)) is True
    assert ask(ambient.is_antichain_of_poset(chain)) is False
    assert ask(ambient.is_chain_of_poset(middle)) is False
    assert ask(ambient.is_antichain_of_poset(middle)) is True


test_induced_subposet_retains_the_exact_poset_and_carrier_inclusions()
test_induced_subposet_constructor_does_not_require_a_finite_ambient()
test_finite_collection_algorithms_return_owned_subobjects()
