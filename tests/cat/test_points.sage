"""Point categories and the level shift (POL-CAT-083, ``specs/functor.md``).

``Cat().Point(X)``, written ``{X}``, is the one-object category whose sole object is
``X`` and whose sole morphism is ``1_X``.  A point functor is its subcategory monomorphism into
a category that already has ``X`` among its objects.

For ``X`` a category ``C``, the surface of the target lands one level down, because
``Cat().ElementType`` is the role "generalized element of a category": its generalized points
points are the objects of ``C`` and its generalized points ``[1] -> C`` are the morphisms of ``C``.
Each row below is one line of the level-shift table.

Oracles: the definition of a one-object category; the definition of a generalized element
as a functor ``T -> C`` (``specs/functor.md``, "Generalized elements"); the level-shift
table in ``specs/functor.md``, "The level shift".  Toy categories live only in this file
(POL-TEST-006).
"""

from sage.rings.integer_ring import ZZ as _integer_ring

from sage_categories.all import *
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


class Marked(Category):
    """A target category declaring one operation on each of its three roles."""

    class DeclaredObjectType(ObjectOfCategory):
        def object_mark(self) -> str:
            return "object"

    class DeclaredElementType(ElementOfObject):
        def element_mark(self) -> str:
            return "element"

    class DeclaredMorphismType(MorphismOfCategory):
        def morphism_mark(self) -> str:
            return "morphism"

    def __repr__(self) -> str:
        return "Marked"


# The subject is ``Cardinal()``: a category that selects a structure functor and whose
# values already exist.  The mechanism exists for categories that take part in the
# structural graph, so every row below is stated on one; a category selecting nothing
# exercises neither the check on its own selection nor installation onto an already
# compiled descendant.  ``Cardinal()`` is also the shape ``Ordinals()`` takes once it
# declares its structure.
#
# One target and one point category, declared here: ``Cat()`` retains one point category
# per object, so a second ``Cat().Point(subject, ...)`` with a different target returns
# the retained one and ignores the new target.
MARKED = Marked()
SUBJECT = Cardinal()
POINT = Cat().Point(SUBJECT, (MARKED,))


def test_a_point_category_is_the_one_object_category_on_its_member() -> None:
    """``{X}`` has ``X`` as its sole object, and ``Cat()`` retains one per object."""
    marked, subject, point = MARKED, SUBJECT, POINT

    assert point.member() is subject
    assert point() is subject
    assert Cat().Point(subject) is point, "one point category per object, retained by identity"
    assert Cat().retained_point(subject) is point, "the same table, read from the member"
    assert point is not Cat().Terminal(), "the terminal category's object is a vertex, not this member"


def test_a_point_functor_is_the_subcategory_monomorphism_of_the_point_category() -> None:
    """``{X}`` selects one point functor per target, constructed through ``Fun({X}, D)``."""
    marked, subject, point = MARKED, SUBJECT, POINT

    selected = point.structure_functors()
    into_marked = [functor for functor in selected if functor.codomain() is marked]

    assert len(into_marked) == int(1), "one point functor per target category"
    assert into_marked[int(0)].domain() is point
    assert into_marked[int(0)] in Mor(Cat()).Faithful(), "every functor out of a one-hom category is faithful"


def test_the_point_functor_supplies_the_object_surface_to_the_member_itself() -> None:
    """Level-shift row 1: ``D.ObjectType`` lands on the category ``C``, a ``Cat().ObjectType`` value."""
    subject = SUBJECT

    assert subject.object_mark() == "object"


def test_the_point_functor_supplies_the_element_surface_one_level_down() -> None:
    """Level-shift rows 2 and 3: ``D.ElementType`` reaches the objects of ``C`` with domain ``1`` and its morphisms with domain ``[1]``."""
    subject = SUBJECT
    three = subject(int(3))
    identity = three.identity()

    assert three.element_mark() == "element", "an object of C is a generalized point 1 -> C"
    assert identity.element_mark() == "element", "a morphism of C is a generalized point [1] -> C"


# -- a point category on a distinguished named object (POL-CAT-083) --
#
# The even integers: a rule, a cited cardinality, and one further placement.  ``{X}``
# supplies the object, element, and morphism roles, the subcategory monomorphism, and
# the constructor returning the sole object.


def _is_even(datum) -> bool:
    """Sage's exact integer ring decides membership and parity at the private boundary."""
    return datum in _integer_ring and Integer(datum) % int(2) == int(0)


# #2ZZ = aleph0: the doubling bijection ZZ -> 2ZZ, with Mathlib ``Cardinal.mk_int``
# (Mathlib.SetTheory.Cardinal.Basic; inspected 2026-08-26) for #ZZ = aleph0.
EVEN_INTEGERS = Sets().with_cardinality(_is_even, aleph0)
EVENS = Cat().Point(EVEN_INTEGERS, (Sets().Countable(),))


def test_the_member_of_a_point_category_is_its_sole_object_and_is_placed_there() -> None:
    """``{X}`` has ``X`` as its sole object, and refining ``X`` into it keeps ``X``'s own membership rule."""
    evens = EVEN_INTEGERS

    assert EVENS() is evens, "the sole object of the point category"
    assert evens.category() is EVENS, "the member is placed in its point category"
    assert ask(evens.membership_proposition(evens.point(Integer(6))))
    assert not ask(evens.membership_proposition(ZZ(int(3))))


def test_a_point_functor_carries_the_cited_placement_and_the_inherited_set_surface() -> None:
    """The point functor places ``X`` in its target; the set surface is compiled from ``Sets()``, not declared."""
    evens = EVEN_INTEGERS

    assert evens in Sets().Countable(), "the placement the point functor installs"
    assert evens in Sets(), "and therefore in the ambient"
    assert ask(evens.cardinality() == aleph0), "the recorded cardinal, read through the Sets() surface"
    assert ask(evens.is_countable())
    assert not ask(evens.is_finite())
