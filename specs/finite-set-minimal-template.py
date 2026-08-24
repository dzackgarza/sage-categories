"""Minimal leaf for the property category ``Sets().Finite()``.

See ``specs/functor.md`` for structural-functor declarations.
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
