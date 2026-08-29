"""Minimal predicate-backed category for finite sets.

This file is design pseudocode (``POL-LEAF-014``). The shape is what it teaches:
nested implementation classes, Sage axiom registration, and the one private abstract predicate
required by ``PredicateSubcategory``. The kernel owns the subcategory monomorphism,
ambient predicate application, and refinement machinery.
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
        """Add no data to a point of a finite set."""

    class MorphismType:
        """Add no data to a map between finite sets."""

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
