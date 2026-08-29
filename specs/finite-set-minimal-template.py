"""Finite-set specimen for the property architecture.

This design pseudocode shows the local ``FiniteSets`` declarations and handler.
See ``property-refinement.md`` and ``undecidable-properties.md`` for their contracts.
"""

from __future__ import annotations


class SetsCategory(Category):
    Finite = Axiom()

    class ObjectType:
        """Implement sets."""

    class ElementType:
        """Implement elements of represented sets."""

    class MorphismType:
        """Implement total set maps."""


class FiniteSets(PredicateSubcategory):
    """The full property subcategory of finite sets."""

    _base_category_class_and_axiom = (SetsCategory, "Finite")

    class ObjectType:
        """Inherit the set surface under established finiteness."""

    class ElementType:
        """Supply no finite-set element operation."""

    class MorphismType:
        """Supply no finite-set morphism operation."""

    def _predicate(
        self,
        X: Sets().ObjectType,
    ) -> Proposition:
        """Return the proposition that ``X`` has finite cardinality."""
        return X.cardinality() < ALEPH_ZERO


def decide_finiteness(X: Sets().ObjectType) -> Decision:
    """Return an exact decision for supported private-engine cases."""
    match X:
        case ExplicitFiniteSet():
            return True
        case ExplicitInfiniteSet():
            return False
        case _:
            return Unknown


FiniteSets().register_exact_handler(
    Sets().ObjectType,
    decide_finiteness,
)
