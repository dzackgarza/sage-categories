"""Predicate subobjects retain membership and inclusion on infinite sets."""

from sympy import Q, Symbol

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


test_predicate_subobject_of_an_infinite_set()
