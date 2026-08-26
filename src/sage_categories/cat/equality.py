"""The equality predicate owned by every category (D17).

Every owned category owns one equality predicate for its objects, its morphisms,
and the elements of its objects.  ``a == b`` on an owned value applies it and
``ask(a == b)`` decides it.  Identity is the first exact positive handler of every
equality predicate; a category registers further exact handlers on the semantic
domains it owns (classical elements of one set, set maps on a finite enumerable
domain, paths of a finitely presented category).  Everything else is ``Unknown``.
"""

from typing import Any

from sage_categories.kernel.decisions import Decision, Unknown
from sage_categories.kernel.predicates import Predicate

__all__ = ["equality_predicate"]


def _identity(first: Any, second: Any) -> Decision:
    if first is second:
        return True
    return Unknown


def equality_predicate() -> Predicate:
    """A fresh equality predicate whose first handler is identity."""
    equal = Predicate("equal", 2, True)
    equal.register_handler(_identity)
    return equal
