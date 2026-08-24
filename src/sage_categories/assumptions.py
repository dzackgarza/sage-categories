"""Owned hypotheses with a private SymPy assumption representation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.values import Decision

if TYPE_CHECKING:
    from sage_categories.category import Category
    from sage_categories.values import MathematicalObject


class Hypothesis:
    """One accepted mathematical proposition."""

    def __init__(self, category: Category, candidate: MathematicalObject) -> None:
        self._category = category
        self._candidate = candidate

    def category(self) -> Category:
        return self._category

    def candidate(self) -> MathematicalObject:
        return self._candidate


class HypothesisContext:
    """A scoped collection of accepted mathematical hypotheses."""

    def __init__(self, *hypotheses: Hypothesis) -> None:
        self._hypotheses = hypotheses

    def establishes(self, hypothesis: Hypothesis) -> Decision:
        return any(accepted is hypothesis for accepted in self._hypotheses)
