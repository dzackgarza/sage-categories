"""``RR``: the set of real numbers, the sole object of ``Reals()``.

``Reals()`` is the one-object category of ``RR`` (POL-CAT-083), a full subcategory
of ``Sets().Uncountable()``.  The cardinality ``continuum = 2 ** aleph0`` is
recorded at construction (POL-MATH-024, POL-LEAF-057).

The private datum of a real point is an element of Sage's field ``AA`` of real
algebraic numbers: the exact real representation Sage supplies with decidable
equality (POL-CODE-017).  The membership rule answers ``True`` for a datum that
``AA`` admits (integers, rationals, and real algebraic data) and ``Unknown``
otherwise: a datum outside ``AA``, such as a transcendental constant, may still be
real, and Sage supplies no exact decision for it.  ``RR(x)`` constructs the point
selecting ``AA(x)``.
"""

from __future__ import annotations

from sage.rings.integer import Integer
from sage.rings.qqbar import AA as _real_algebraic_field
from sage.rings.qqbar import AlgebraicReal
from sage.rings.rational import Rational

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.cardinals import continuum
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import SetObject

__all__ = ["RR", "Reals", "RealsCategory"]


def _is_real(datum: Datum) -> Decision:
    """``AA`` decides membership positively; no exact negative decision is available."""
    if datum in _real_algebraic_field:
        return True
    return Unknown


class RealSet(ObjectOfCategory):
    """The local object role of ``Reals()``: ``RR(x)`` is the point selecting ``AA(x)``."""

    def __call__(self, real: int | Integer | Rational | AlgebraicReal) -> SetElement:
        return self.point(_real_algebraic_field(real))

    def __repr__(self) -> str:
        return "RR"


class RealsCategory(Category[[Rule], []]):
    """The one-object category of ``RR``, a full subcategory of ``Sets().Uncountable()``."""

    DeclaredObjectType = RealSet

    class DeclaredElementType(ElementOfObject):
        """A generalized element of ``RR``; no local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        """A map ``RR -> RR``; no local operation."""

    def __init__(self) -> None:
        super().__init__()
        # #RR = continuum = 2 ** aleph0: Mathlib ``Cardinal.mk_real`` (Mathlib.Analysis.Real.Cardinality)
        # and ``Cardinal.continuum`` (Mathlib.SetTheory.Cardinal.Continuum); inspected 2026-08-26.
        self._reals = Sets().with_cardinality(_is_real, continuum)
        refine(self._reals, self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, Sets().Uncountable()).FullyFaithful().inclusion(),)

    def __call__(self) -> SetObject:
        """The sole object ``RR``, retained by identity."""
        return self._reals

    def __repr__(self) -> str:
        return "Reals"


_REALS = RealsCategory()


def Reals() -> RealsCategory:
    """The one-object category of the real numbers."""
    return _REALS


RR = Reals()()
