"""The equality predicate owned by every category (POL-MATH-034, POL-SET-026).

Every owned category owns one equality predicate for its objects, its morphisms,
and the elements of its objects.  ``a == b`` on an owned value applies it and
``ask(a == b)`` decides it.  Identity is the first exact positive handler of every
equality predicate; a category registers further exact handlers on the semantic
domains it owns (classical elements of one set, set maps on a finite enumerable
domain, paths of a finitely presented category).  Everything else is ``Unknown``.
"""

from typing import Any

from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import EqualityPredicate
from sage_categories.kernel.roles import CategoryPoint

__all__ = ["equality_predicate"]


def _identity(first: CategoryPoint, candidate: Any) -> Decision:
    if first is candidate:
        return True
    return Unknown


def equality_predicate() -> EqualityPredicate:
    """A fresh equality predicate whose first handler is identity."""
    equal = EqualityPredicate("equal")
    equal.register_handler(_identity)
    return equal
