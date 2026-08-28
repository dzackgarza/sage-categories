"""Minimal structured leaf for ``PartiallyOrderedSets()``.

This file is design pseudocode (``POL-LEAF-014``). Its identifiers show the
required contract. They do not define a second framework API.

A public call accepts a plain Python set ``X_prime`` and an order callable.
It constructs the poset ``(X, R)``, where ``X = Sets()(X_prime)`` and ``R`` is
the relation defined by the callable. The named projection ``(X, R) |-> X`` is
an ordinary functor. It is the only structure functor.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PosetConstructionData:
    """The exact semantic input for one poset construction."""

    elements: set[SetElement]
    order_rule: OrderRule


class PartiallyOrderedSetsCategory(Category):
    """The category of partially ordered sets and monotone maps."""

    class ObjectType:
        """Implement only the order structure added to the set."""

        def __init__(self, data: PosetConstructionData) -> None:
            self._order_relation = relation_subobject(
                data.elements,
                data.order_rule,
            )
            super().__init__()

        def order_relation(self) -> SetSubset:
            """Return the defining subobject of ``X * X``."""
            return self._order_relation

    class ElementType:
        """Add order comparison to points of a poset."""

        def __le__(
            self,
            other: PartiallyOrderedSetsCategory.ElementType,
        ) -> Proposition:
            """Return the proposition ``self <= other``."""
            assert other.parent() is self.parent()
            return self.parent().order_relation().contains_pair(self, other)

    class MorphismType:
        """Implement monotone maps."""

    def __call__(
        self,
        X_prime: set[SetElement],
        order_rule: OrderRule,
    ) -> PartiallyOrderedSetsCategory.ObjectType:
        """Construct the asserted partial order on ``X_prime``."""
        data = PosetConstructionData(
            elements=X_prime,
            order_rule=order_rule,
        )
        return self.ObjectType(data)

    def set_projection(self) -> Cat().MorphismType:
        """Return the projection ``(X, R) |-> X``."""

        def set_constructor_input(
            data: PosetConstructionData,
        ) -> SetsConstructorInput:
            return SetsConstructorInput.from_python_set(data.elements)

        # The functor retains ``set_constructor_input`` once. Its public object
        # action and the kernel's ``Sets.ObjectType`` initialization both use it.
        return Fun(self, Sets())(
            object_constructor_input=set_constructor_input,
            on_morphism=set_projection_on_morphism,
            terminal_comparison=terminal_point_comparison,
        )

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the set projection for inherited set operations."""
        return (self.set_projection(),)
