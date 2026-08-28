"""Minimal property category for finite sets.

This file is design pseudocode (``POL-LEAF-014``). The shape is what it teaches:
nested implementation classes, one axiom field, one predicate declaration, one
membership proposition, and one structure functor. Its identifiers are illustrative
and define no second framework API.
"""

from __future__ import annotations


class SetsCategory(Category):
    class ObjectType:
        """Implement sets."""

    class ElementType:
        """Implement points ``1 -> X`` of sets."""

    class MorphismType:
        """Implement total set maps."""


class FiniteSets(CategoryWithAxiom):
    """The full property subcategory of finite sets."""

    _base_category_class_and_axiom = (SetsCategory, "Finite")
    predicate_name = "is_finite"
    predicate_owner = SetsCategory.ObjectType

    class ObjectType:
        """Inherit the set surface under established finiteness."""

    class ElementType:
        """Add no data to a point of a finite set."""

    class MorphismType:
        """Add no data to a map between finite sets."""

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the full subcategory monomorphism into ``Sets()``."""
        return (Fun(self, Sets()).Monomorphisms().Isofibrations().Full()(),)

    def membership_proposition(
        self,
        X: SetsCategory.ObjectType,
    ) -> Proposition:
        """Return the proposition that ``X`` has finite cardinality."""
        return self.applied_predicate(
            X,
            definition=X.cardinality() < ALEPH_ZERO,
        )


def decide_finiteness(X: SetsCategory.ObjectType) -> Decision:
    """Return an exact decision for supported private-engine cases."""
    match X:
        case ExplicitFiniteSet():
            return True
        case ExplicitInfiniteSet():
            return False
        case _:
            return Unknown


FiniteSets().register_exact_handler(
    SetsCategory.ObjectType,
    decide_finiteness,
)
