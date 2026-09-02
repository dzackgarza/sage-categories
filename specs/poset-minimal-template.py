"""Local declarations for one ``Posets()`` design specimen.

This pseudocode constructs a poset from its relation subobject ``R -> X * X``.
It selects the retained first projection ``(X, R) |-> X`` to ``Sets()``.
"""

from __future__ import annotations

from collections.abc import Callable

from sympy.logic.boolalg import Boolean


class PosetsCategory(Category):
    """Implement posets and monotone maps."""

    class ObjectType:
        """Add the operations the order relation supplies."""

        def __init__(self, relation: Sets().Subobjects(X * X).ObjectType) -> None:
            """Retain the relation subobject; its codomain ``X * X`` determines ``X``."""
            self._relation = relation

    class ElementType:
        """Add order comparison to points of a poset."""

        def __le__(self, other: Posets().ElementType) -> Boolean:
            """Return the proposition ``self <= other``."""
            return self.parent()._relation.membership_proposition((self, other))

    class MorphismType:
        """Implement monotone maps."""

    def __call__(self, relation: Sets().Subobjects(X * X).ObjectType) -> Posets().ObjectType:
        """Construct the poset with order relation ``relation``."""
        return self.ObjectType(relation)

    def from_predicate(
        self,
        X: Sets().ObjectType,
        predicate: Callable[[Sets().ElementType, Sets().ElementType], Boolean],
    ) -> Posets().ObjectType:
        """Construct the poset whose relation subobject ``predicate`` selects in ``X * X``."""
        return self(Sets().Subobjects(X * X).from_predicate(predicate))

    def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
        """Select the first projection ``(X, R) |-> X`` for inherited set operations.

        A poset inherits the structure of its set ``X``, so only the first projection
        is selected. The projection to ``R`` stays an ordinary retained functor.
        """
        return (self.product_projection(0),)
