"""Minimal leaf for the property category ``Sets().Finite()``.

See ``specs/functor.md`` for structural-functor declarations.
"""

from __future__ import annotations


class SetsCategory(Category):
    class ObjectType(Implementation):
        def is_finite(self) -> Proposition:
            """Return the finite-set membership proposition."""
            return Sets().Finite().membership_proposition(self)

    class Finite(Category):
        """The full property subcategory of finite sets."""

        def structure_functors(self) -> tuple[Cat().ArrowType, ...]:
            """Select the inclusion that supplies the inherited set catalogue.

            This tuple is not a list of all functors from finite sets.
            The kernel-owned inclusion supplies its required maps. Other functors
            from finite sets remain ordinary objects of ``Ar(Cat())``.
            """
            return (self.inclusion(Sets()),)

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
            """Implement only the operations introduced by known finiteness.

            No initializer repeats set construction. The kernel-owned inclusion
            supplies the canonical ``Sets().ObjectType`` image.
            """

            def cardinality_parity(self) -> Proposition:
                """Return the proposition that the cardinality is even."""
                return self.cardinality() % 2 == 0


FiniteSets = SetsCategory.Finite
