"""``ZZ``: the set of integers, the sole object of the named-object leaf ``Integers()``.

``Integers()`` is the one-object category of ``ZZ`` (POL-CAT-083): a full
subcategory of ``Sets().Countable()`` whose one selected subcategory monomorphism places ``ZZ``
there and supplies the complete set surface.  ``ZZ`` is rule-defined: a datum is a
member exactly when Sage's exact integer ring admits it at the private boundary,
and its cardinality ``aleph0`` is recorded at construction (POL-MATH-024,
POL-LEAF-057).  ``ZZ(n)`` constructs the point ``1 -> ZZ`` selecting the Sage
integer ``n``.
"""

from __future__ import annotations

from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ as _integer_ring
from sage.rings.qqbar import QQbar as _algebraic_numbers

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.cardinals import aleph0
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import SetObject

__all__ = ["ZZ", "Integers", "IntegersCategory"]


def _is_integer(datum: Datum) -> Decision:
    """Sage's exact integer ring decides membership; the algebraic numbers carry the negative decision.

    ``QQbar`` is the algebraic closure of ``QQ`` and "all computations are exact"
    (``sage/rings/qqbar.py``, module docstring; inspected 2026-08-28), so an
    algebraic number that ``ZZ`` does not admit is exactly not an integer.  That
    field is the whole declared semantic domain of the negative decision: outside
    it, whether a symbolic constant is an integer can be an open problem, and an
    open problem is ``Unknown``, not ``False`` (POL-MATH-042).
    """
    if datum in _integer_ring:
        return True
    if datum in _algebraic_numbers:
        return False
    return Unknown


class IntegerSet(ObjectOfCategory):
    """The local object role of ``Integers()``: ``ZZ(n)`` is the point selecting ``n``."""

    def __call__(self, integer: int | Integer) -> SetElement:
        return self.point(Integer(integer))

    def __repr__(self) -> str:
        return "ZZ"


class IntegersCategory(Category[[Rule], []]):
    """The one-object category of ``ZZ``, a full subcategory of ``Sets().Countable()``."""

    DeclaredObjectType = IntegerSet

    class DeclaredElementType(ElementOfObject):
        """A generalized element of ``ZZ``; no local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        """A map ``ZZ -> ZZ``; no local operation."""

    def __init__(self) -> None:
        super().__init__()
        # #ZZ = aleph0: Mathlib ``Cardinal.mk_int`` (Mathlib.SetTheory.Cardinal.Basic; inspected 2026-08-26).
        self._integers = Sets().with_cardinality(_is_integer, aleph0)
        refine(self._integers, self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, Sets().Countable()).Monomorphisms().Isofibrations().Full()(),)

    def __call__(self) -> SetObject:
        """The sole object ``ZZ``, retained by identity."""
        return self._integers

    def __repr__(self) -> str:
        return "Integers"


_INTEGERS = IntegersCategory()


def Integers() -> IntegersCategory:
    """The one-object category of the integers."""
    return _INTEGERS


ZZ: SetObject = Integers()()
