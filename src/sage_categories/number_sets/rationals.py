"""``QQ``: the set of rational numbers, the sole object of ``Rationals()``.

``Rationals()`` is the one-object category of ``QQ`` (POL-CAT-083), a full
subcategory of ``Sets().Countable()``.  A datum is a member exactly when Sage's
exact rational field admits it at the private boundary; the cardinality
``aleph0`` is recorded at construction (POL-MATH-024, POL-LEAF-057).  ``QQ(q)``
constructs the point selecting the Sage rational ``q``.
"""

from __future__ import annotations

from sage.rings.integer import Integer
from sage.rings.rational import Rational
from sage.rings.rational_field import QQ as _rational_field

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.kernel.decisions import Decision
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.cardinals import aleph0
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetPoint
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import SetObject

__all__ = ["QQ", "Rationals", "RationalsCategory"]


def _is_rational(datum: Datum) -> Decision:
    """Sage's exact rational field decides membership of a datum at the private boundary."""
    return datum in _rational_field


class RationalSet(ObjectOfCategory):
    """The local object role of ``Rationals()``: ``QQ(q)`` is the point selecting ``q``."""

    def __call__(self, rational: int | Integer | Rational) -> SetPoint:
        return self.point(Rational(rational))

    def __repr__(self) -> str:
        return "QQ"


class RationalsCategory(Category[[Rule], []]):
    """The one-object category of ``QQ``, a full subcategory of ``Sets().Countable()``."""

    ObjectType = RationalSet

    class ElementType(ElementOfObject):
        """A generalized element of ``QQ``; no local operation."""

    class MorphismType(MorphismOfCategory):
        """A map ``QQ -> QQ``; no local operation."""

    def __init__(self) -> None:
        super().__init__()
        # #QQ = aleph0: Mathlib ``Cardinal.mkRat : #ℚ = ℵ₀`` (``Mathlib/SetTheory/Cardinal/Rat.lean``; inspected 2026-08-27).
        self._rationals = self.ObjectType(self, _is_rational, aleph0)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, Sets().Countable()).FullyFaithful().inclusion(),)

    def __call__(self) -> SetObject:
        """The sole object ``QQ``, retained by identity."""
        return self._rationals

    def __repr__(self) -> str:
        return "Rationals"


_RATIONALS = RationalsCategory()


def Rationals() -> RationalsCategory:
    """The one-object category of the rational numbers."""
    return _RATIONALS


QQ = Rationals()()
