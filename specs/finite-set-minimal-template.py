"""Finite-set design specimen for the public SymPy proposition contract.

This pseudocode shows only the declarations owned by ``Sets().Finite()``.
The private atom adapter and class compiler belong to the runtime substrate.
"""

from __future__ import annotations

from sympy.assumptions import Predicate
from sympy.logic.boolalg import Boolean


class FinitePredicate(Predicate):
    """State that an owned set has finite cardinality."""

    name = "finite"


finite = FinitePredicate()


class SetsCategory(Category):
    Finite = Axiom(predicate=finite)

    class ObjectType:
        """Implement sets."""

    class ElementType:
        """Implement elements of represented sets."""

    class MorphismType:
        """Implement total set maps."""


class FiniteSetsCategory(Category):
    """Implement the full property subcategory of finite sets."""

    _base_category_class_and_axiom = (SetsCategory, "Finite")

    class ObjectType:
        """Inherit the set surface under established finiteness."""

    class ElementType:
        """Add no finite-set element operation."""

    class MorphismType:
        """Add no finite-set morphism operation."""

    def membership_proposition(self, X: Sets().ObjectType) -> Boolean:
        """Apply the category-owned predicate without evaluation."""
        return finite(owned_value_atom(X))


@finite.register(OwnedValueAtom)
def decide_finiteness(
    X: OwnedValueAtom,
    assumptions: Boolean,
) -> bool | None:
    """Decide finiteness for exact supported owned representations."""
    value = X.owned_value()
    match value:
        case ExplicitFiniteSet():
            return True
        case ExplicitInfiniteSet():
            return False
        case _:
            return None
