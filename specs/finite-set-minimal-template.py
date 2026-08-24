"""Normative minimal leaf for the property category ``Sets().Finite()``.

The nested property declaration determines the full replete inclusion

    Sets().Finite() -> Sets().

The kernel takes the source from the nested category. It takes the target from
the enclosing category. It supplies the identity action on objects, elements,
and arrows. It also supplies containment, construction, assumptions,
refinement, and propagation to structural subcategories.

``FiniteSets()`` and ``Sets().Finite()`` denote the same category.
"""

from __future__ import annotations


class SetsCategory(Category):
    class ObjectType(Implementation):
        def is_finite(self) -> Proposition:
            """Return the finite-set membership proposition."""
            return Sets().Finite().membership_proposition(self)

    class Finite(FullRepletePropertySubcategory):
        """The full replete subcategory of finite sets."""

        def membership_proposition(
            self,
            X: SetsCategory.ObjectType,
        ) -> Proposition:
            """Return the proposition that ``X`` has finite cardinality."""
            return self.applied_predicate(
                X,
                definition=X.cardinality() < ALEPH_ZERO,
            )

        class ObjectType(Implementation):
            """Implement the operations introduced by known finiteness."""

            def cardinality_parity(self) -> Proposition:
                """Return the proposition that the cardinality is even."""
                return self.cardinality() % 2 == 0


FiniteSets = SetsCategory.Finite


# Kernel-derived public behavior:
#
# Sets().Finite().inclusion().domain()   is Sets().Finite()
# Sets().Finite().inclusion().codomain() is Sets()
# Sets().Finite().inclusion().on_object(X)   is X
# Sets().Finite().inclusion().on_morphism(f) is f
#
# X.cardinality() is inherited from Sets.ObjectType.
# X.is_finite() constructs a proposition.
# ask(X.is_finite()) decides it when exact knowledge is available.
# Sets().Finite()(X) places X directly in the property category.
