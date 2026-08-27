"""Kernel-owned retention: a category's chosen datum, and one result per argument sequence.

Two constructions in this repository need a table keyed by owned values, and neither is a
leaf's to write (``specs/resolution.md``, final decision 6).

A category whose constructor refines an existing value in place adds no construction input
of its own (``kernel/refinement.py``), so the structure it chose -- a base set, an
enumeration engine, a basepoint -- is retained by ``C.retain_datum`` and read back by
``C.retained_datum`` (POL-KERNEL-001).

A construction that returns one value for its data retains that value with
``retained_method``.  This is Sage's ``cached_method`` with the comparison the arguments
admit: equality between owned values here is a proposition that can be undecided
(``specs/sets.md``, "Equality"), so an owned argument is compared by identity and an index
or size by equality.

Oracles: the definition of a chosen structure (one per value, fixed at construction); the
identity criterion for constructed values (POL-CAT-066); extensionality for the two equal
sets below (Mathlib ``Set.ext_iff``, ``Mathlib/Data/Set/Defs.lean``; inspected 2026-08-28).
Toy categories live only in this file (POL-TEST-006).
"""

import pytest

from sage_categories.all import *
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.kernel.caches import retained_method
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ObjectOfCategory, Role


class PointedRole(ObjectOfCategory):
    """The local object role of the toy: the basepoint its constructor chose."""

    def basepoint(self):
        return POINTED.retained_datum(self)


class PointedSets(PropertySubcategory):
    """``Sets().Pointed()``: a set of ``Sets()`` together with a chosen point of it.

    Its constructor refines the very same set object, so the chosen point has nowhere to
    live but the retention this category owns.
    """

    def __init__(self):
        super().__init__(Sets(), "Pointed", {Role.OBJECT: PointedRole}, ())

    def __call__(self, base_set, basepoint):
        assert basepoint.parent() is base_set, f"{basepoint!r} is not a point of {base_set!r}"
        refine(base_set, self)
        self.retain_datum(base_set, basepoint)
        return base_set


POINTED = PointedSets()


class Segmenting(Category):
    """A toy owning one construction: the chosen set of the first ``bound`` indices."""

    @retained_method
    def initial_segment(self, base_set, bound):
        """``{0, ..., bound - 1}``, one value per ``(base_set, bound)``."""
        return Sets().Finite()(tuple(range(bound)))

    def __repr__(self) -> str:
        return "Segmenting"


SEGMENTING = Segmenting()


# -- the chosen datum a refining constructor retains --------------------------------------


def test_a_refining_constructor_retains_its_chosen_structure_on_the_same_value() -> None:
    """``C(X, x)`` returns the very object ``X`` of ``Sets()``, and ``X`` answers with the chosen point."""
    members = Sets().Finite()((int(0), int(1)))
    chosen = members.point(int(1))

    assert POINTED(members, chosen) is members, "a property subcategory refines in place; it builds no second value"
    assert members in POINTED and members in Sets()
    assert members.basepoint() is chosen, "the role method reads the datum the constructor retained"


def test_each_value_retains_its_own_chosen_structure() -> None:
    """The retention is keyed by the value, so two pointed sets keep two distinct basepoints."""
    first, second = Sets().Finite()((int(0), int(1))), Sets().Finite()((int(0), int(1)))
    first_point, second_point = first.point(int(0)), second.point(int(1))
    POINTED(first, first_point)
    POINTED(second, second_point)

    assert first.basepoint() is first_point
    assert second.basepoint() is second_point
    assert ask(first == second) is True, "extensionality: equal sets, and still two chosen points"


def test_a_value_that_entered_no_such_constructor_retains_no_datum() -> None:
    """A set of ``Sets()`` alone has chosen no point, and the retention says so rather than inventing one."""
    plain = Sets().Finite()((int(2), int(3)))

    with pytest.raises(AssertionError):
        POINTED.retained_datum(plain)


# -- one result per argument sequence ------------------------------------------------------


def test_a_retained_construction_returns_one_value_for_one_argument_sequence() -> None:
    """``initial_segment(X, 2)`` names one set, not an equal second copy (POL-CAT-066)."""
    members = Sets().Finite()((int(0), int(1)))

    assert SEGMENTING.initial_segment(members, int(2)) is SEGMENTING.initial_segment(members, int(2))
    assert ask(SEGMENTING.initial_segment(members, int(2)).cardinality() == int(2)) is True


def test_a_retained_construction_separates_argument_sequences_that_differ() -> None:
    """A different bound is different data and names a different set."""
    members = Sets().Finite()((int(0), int(1)))
    two, three = SEGMENTING.initial_segment(members, int(2)), SEGMENTING.initial_segment(members, int(3))

    assert two is not three
    assert ask(three.cardinality() == int(3)) is True


def test_an_owned_argument_is_compared_by_identity_and_not_by_equality() -> None:
    """Two sets with the same members are equal and are distinct values; each keeps its own result."""
    first = Sets().Finite()((int(0), int(1)))
    second = Sets().Finite()((int(0), int(1)))

    assert first is not second
    assert ask(first == second) is True, "extensionality: the same members"
    assert SEGMENTING.initial_segment(first, int(2)) is not SEGMENTING.initial_segment(second, int(2))


def test_a_position_argument_is_compared_by_equality() -> None:
    """A bound carries its whole meaning, so two equal bounds select one retained result."""
    members = Sets().Finite()((int(0), int(1)))
    bound, same_bound = int(300), int(299) + int(1)

    assert bound is not same_bound and bound == same_bound, "two distinct Python integers of one value"
    assert SEGMENTING.initial_segment(members, bound) is SEGMENTING.initial_segment(members, same_bound)
