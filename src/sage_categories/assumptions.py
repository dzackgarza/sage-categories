"""Owned hypotheses with a private SymPy assumption representation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Predicate, Symbol
from sympy.assumptions.assume import AssumptionsContext as SymPyAssumptionsContext
from sympy.assumptions.ask import ask

from sage_categories.values import UNKNOWN, Decision

if TYPE_CHECKING:
    from sage_categories.category import Category
    from sage_categories.values import MathematicalObject


class Hypothesis:
    """One accepted mathematical proposition."""

    def __init__(self, category: Category, candidate: MathematicalObject) -> None:
        self._category = category
        self._candidate = candidate
        predicate = Predicate(f"membership_{id(category)}")
        self._predicate = predicate(Symbol(f"value_{id(candidate)}"))

    def category(self) -> Category:
        return self._category

    def candidate(self) -> MathematicalObject:
        return self._candidate


class HypothesisContext:
    """A scoped collection of accepted mathematical hypotheses."""

    def __init__(self, *hypotheses: Hypothesis) -> None:
        # SymPy's explicit AssumptionsContext is the maintained assumption
        # engine described in its assumptions module documentation.
        self._context = SymPyAssumptionsContext(
            hypothesis._predicate for hypothesis in hypotheses
        )

    def establishes(self, hypothesis: Hypothesis) -> Decision:
        answer = ask(hypothesis._predicate, context=self._context)
        if answer is None:
            return UNKNOWN
        return bool(answer)
