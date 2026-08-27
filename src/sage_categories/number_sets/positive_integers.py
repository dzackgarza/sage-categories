"""``NN``: the set of positive integers, the sole object of ``PositiveIntegers()``.

Zero is not an element of ``NN`` (POL-SET-032).  ``PositiveIntegers()`` is the
one-object category of ``NN`` (POL-CAT-083), a full subcategory of
``Sets().Countable()``.  A datum is a member exactly when Sage's exact integer ring
admits it and it is positive; the cardinality ``aleph0`` is recorded at construction
(POL-MATH-024, POL-LEAF-057).  ``NN(n)`` constructs the point selecting the Sage
integer ``n``.
"""

from __future__ import annotations

from sage.rings.integer import Integer

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Fun, Functor
from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.number_sets.integers import _is_integer
from sage_categories.sets.cardinals import aleph0
from sage_categories.sets.category import Sets
from sage_categories.sets.elements import Datum, SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import SetObject

__all__ = ["NN", "PositiveIntegers", "PositiveIntegersCategory", "natural_order"]


def _is_positive_integer(datum: Datum) -> Decision:
    """Integrality decides first; on an established integer the exact order decides positivity.

    ``ZZ`` owns the integrality decision (``number_sets/integers.py``), so ``NN``
    states only its new mathematics.  Positivity is asked only of a datum that ``ZZ``
    admits, where ``>`` is the exact integer order; an undecided integrality leaves
    membership undecided, since a datum not known to be an integer is not known to be
    a positive integer (POL-MATH-042).
    """
    integrality = _is_integer(datum)
    if integrality is not True:
        return integrality
    return bool(datum > 0)


class PositiveIntegerSet(ObjectOfCategory):
    """The local object role of ``PositiveIntegers()``: ``NN(n)`` is the point selecting ``n``."""

    def __call__(self, integer: int | Integer) -> SetElement:
        return self.point(Integer(integer))

    def __repr__(self) -> str:
        return "NN"


class PositiveIntegersCategory(Category[[Rule], []]):
    """The one-object category of ``NN``, a full subcategory of ``Sets().Countable()``."""

    DeclaredObjectType = PositiveIntegerSet

    class DeclaredElementType(ElementOfObject):
        """A generalized element of ``NN``; no local operation."""

    class DeclaredMorphismType(MorphismOfCategory):
        """A map ``NN -> NN``; no local operation."""

    def __init__(self) -> None:
        super().__init__()
        # #NN = aleph0: Mathlib ``Cardinal.mk_pnat`` (Mathlib.SetTheory.Cardinal.Basic; inspected 2026-08-26).
        self._positive_integers = Sets().with_cardinality(_is_positive_integer, aleph0)
        refine(self._positive_integers, self)

    def structure_functors(self) -> tuple[Functor, ...]:
        return (Fun(self, Sets().Countable()).Monomorphisms().Isofibrations().Full()(),)

    def __call__(self) -> SetObject:
        """The sole object ``NN``, retained by identity."""
        return self._positive_integers

    def __repr__(self) -> str:
        return "PositiveIntegers"


_POSITIVE_INTEGERS = PositiveIntegersCategory()

# ``natural_order(m, n)``: ``m <= n`` for two points of ``NN``, decided by Sage's exact
# integer order; ``omega = Thin(NN, natural_order)`` is the sequential shape (specs/functor.md, "Diagram shapes and universal constructions").
natural_order: Predicate = Predicate("natural_order", 2, True)


def _natural_order_by_integer_comparison(first: CategoryPoint, second: CategoryPoint) -> Decision:
    if first not in _POSITIVE_INTEGERS() or second not in _POSITIVE_INTEGERS():
        return Unknown
    return bool(first._point_datum_() <= second._point_datum_())


natural_order.register_handler(_natural_order_by_integer_comparison)


def PositiveIntegers() -> PositiveIntegersCategory:
    """The one-object category of the positive integers."""
    return _POSITIVE_INTEGERS


NN: SetObject = PositiveIntegers()()
