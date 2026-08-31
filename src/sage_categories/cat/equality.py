"""The equality predicate owned by every category (POL-MATH-034, POL-SET-026).

Every owned category owns one equality predicate for its objects, its morphisms,
and the elements of its objects.  ``a == b`` on an owned value applies it and
``ask(a == b)`` decides it.  Identity is the first exact positive handler of every
equality predicate; a category registers further exact handlers on the semantic
domains it owns (points of one set, set maps on a finite enumerable
domain, paths of a finitely presented category).  Everything else is ``Unknown``.
"""

from __future__ import annotations

from sage_categories.cat.predicates import Decision, Unknown
from sage_categories.cat.predicates import EqualityPredicate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["equality_predicate"]


def _identity(first: CategoryOfCategories.ElementType, candidate: CategoryOfCategories.ElementType) -> Decision:
    if first is candidate:
        return True
    return Unknown


def equality_predicate() -> EqualityPredicate:
    """A fresh equality predicate whose first handler is identity."""
    equal = EqualityPredicate("equal")
    equal.register_handler(_identity)
    return equal
