"""Predicate subobjects retain membership and inclusion on infinite sets."""

from sympy import Q, Rational, Symbol

from sage_categories.all import Mor, Sets, Unknown, ask


def test_predicate_subobject_of_an_infinite_set() -> None:
    integers = Sets.from_membership(Q.integer)
    bound = Symbol("bound", integer=True)
    subobjects = Sets.Subobjects(integers)
    subset = subobjects.from_predicate(lambda point: Q.even(point.datum()) & Q.positive(bound))
    inclusion = subobjects.defining_arrow().on_object(subset)
    selected = inclusion.domain()

    assert inclusion in Mor(Sets).Monomorphisms()
    assert inclusion.codomain() is integers
    assert ask(selected.membership_proposition(integers.point(3))) is False
    assert ask(selected.membership_proposition(integers.point(4))) is Unknown

    even_subset = subobjects.from_predicate(lambda point: Q.even(point.datum()))
    even_inclusion = subobjects.defining_arrow().on_object(even_subset)
    evens = even_inclusion.domain()
    assert ask(evens.membership_proposition(integers.point(4))) is True
    assert ask(evens.membership_proposition(integers.point(3))) is False
    assert even_inclusion(evens.point(4)) is integers.point(4)

    doubling = Mor(Sets)(integers, integers)(lambda value: 2 * value)
    image_predicate = subobjects.from_predicate(lambda point: Q.even(doubling(point).datum()))
    image_subset = subobjects.defining_arrow().on_object(image_predicate).domain()
    outside = Sets((Rational(1, 2),)).point(Rational(1, 2))
    assert ask(image_subset.membership_proposition(outside)) is False

    nested_subobjects = Sets.Subobjects(selected)
    nested = nested_subobjects.from_predicate(lambda point: Q.even(inclusion(point).datum()))
    nested_subset = nested_subobjects.defining_arrow().on_object(nested).domain()
    assert ask(nested_subset.membership_proposition(integers.point(4))) is Unknown
    assert ask(nested_subset.set_presentation()(4)) is Unknown

    finite_ambient = Sets((1, 2, 3))
    finite_subobjects = Sets.Subobjects(finite_ambient)
    finite_subobject = finite_subobjects.from_predicate(lambda point: Q.even(point.datum()) & Q.positive(bound))
    finite_subset = finite_subobjects.defining_arrow().on_object(finite_subobject).domain()
    assert ask(finite_subset.is_finite()) is True
    assert Sets.chosen_enumeration(finite_subset) is Unknown


test_predicate_subobject_of_an_infinite_set()
