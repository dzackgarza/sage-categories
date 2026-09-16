"""Private Sage and FinSetsForCAP conversion boundary for ``Sets``."""

from __future__ import annotations

from sage.rings.integer import Integer as SageInteger
from sage.symbolic.expression import Expression as SageExpression
from sympy import Lambda


def finite_sets():
    from sage_categories.engines import finite_sets as engine

    return engine


def is_sage_integer(value: object) -> bool:
    return isinstance(value, SageInteger)


def symbolic_lambda(value: object) -> Lambda | None:
    """Convert a Sage callable symbolic expression to its SymPy lambda form."""
    if not isinstance(value, SageExpression) or not value.arguments():
        return None
    converted = value._sympy_()
    return converted if isinstance(converted, Lambda) else None
