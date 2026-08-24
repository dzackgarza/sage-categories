"""Normative minimal leaf for the property category ``Sets().Finite()``.

The property category explicitly selects its full-subcategory inclusion

    Sets().Finite() -> Sets()

in ``structure_functors()``. The inclusion constructor receives its source and
target. It supplies the canonical action on objects, elements, and arrows.
The kernel uses the selected functor for inheritance and property propagation.

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

        def structure_functors(self) -> tuple[Functor, ...]:
            """Return the selected functors from finite sets."""
            iota = FullSubcategoryInclusion(self, Sets())
            return (iota,)

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


# Public behavior:
#
# iota = Sets().Finite().structure_functors()[0]
# iota.domain() is Sets().Finite()
# iota.codomain() is Sets()
# iota.on_object(X) is X
# iota.on_morphism(f) is f
#
# X.cardinality() is inherited from Sets.ObjectType.
# X.is_finite() constructs a proposition.
# ask(X.is_finite()) decides it when exact knowledge is available.
# Sets().Finite()(X) places X directly in the property category.
