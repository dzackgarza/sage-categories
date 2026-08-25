"""Owned applied predicates in the active SymPy assumption session."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Predicate, Q, Symbol
from sympy.assumptions import global_assumptions
from sympy.assumptions.assume import AppliedPredicate
from sympy.logic.boolalg import Not

from sage_categories.values import Decision, UNKNOWN

if TYPE_CHECKING:
    from sage_categories.abstract_categories.full_subcategories import FullSubcategory
    from sage_categories.values import MathematicalObject


class OwnedPropertyPredicate(Predicate):
    """The SymPy predicate for an owned property-category statement."""

    name = "owned_property"


Q.owned_property = OwnedPropertyPredicate()


class AppliedProperty:
    """A property-category predicate applied to one owned value."""

    def __init__(
        self,
        category: FullSubcategory,
        candidate: MathematicalObject,
    ) -> None:
        self._category = category
        self._candidate = candidate
        self._engine_value = Q.owned_property(
            Symbol(f"category_{id(category)}"),
            Symbol(f"owned_value_{id(candidate)}"),
        )

    def category(self) -> FullSubcategory:
        return self._category

    def candidate(self) -> MathematicalObject:
        return self._candidate

    def engine_value(self) -> AppliedPredicate:
        return self._engine_value

    def __invert__(self) -> NegatedProperty:
        return NegatedProperty(self)


class NegatedProperty:
    """The negation of one applied property predicate."""

    def __init__(self, positive: AppliedProperty) -> None:
        self._positive = positive

    def positive(self) -> AppliedProperty:
        return self._positive

    def engine_value(self) -> Not:
        return Not(self._positive.engine_value())


type AssumableProperty = AppliedProperty | NegatedProperty


def assume(proposition: AssumableProperty) -> None:
    """Record ``proposition`` and apply positive property refinement."""
    global_assumptions.add(proposition.engine_value())
    if isinstance(proposition, AppliedProperty):
        proposition.category()(proposition.candidate())


def assumption_decision(proposition: AppliedProperty) -> Decision:
    """Return the decision recorded in the active SymPy session."""
    if proposition.engine_value() in global_assumptions:
        return True
    if Not(proposition.engine_value()) in global_assumptions:
        return False
    return UNKNOWN
