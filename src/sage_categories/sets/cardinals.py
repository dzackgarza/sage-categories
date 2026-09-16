"""Owned finite cardinals used by exact finite mathematical consumers.

This module supplies the finite part of the cardinal surface: one category of
nonnegative cardinal values, including zero.  Finite algorithms reconstruct into
these owned values instead of returning Python or Sage integers.  Infinite-cardinal
arithmetic belongs to the broader cardinality owner and is not synthesized here.
"""

from __future__ import annotations

__all__ = ["Cardinal", "CardinalCategory"]

from sage_categories.cat.category import Category
from sage_categories.cat.predicates import Proposition, register_handler


class CardinalCategory(Category):
    """The category owning the represented finite cardinal numbers."""

    class ObjectType:
        """A nonnegative finite cardinal."""

        def __init__(self, value: int) -> None:
            assert value >= 0
            self._cardinal_value = value

        def value(self) -> int:
            return self._cardinal_value

        def __int__(self) -> int:
            return self._cardinal_value

        def __index__(self) -> int:
            return self._cardinal_value

        def __repr__(self) -> str:
            return str(self._cardinal_value)

    class ElementType:
        """A generalized element of a cardinal object."""

    class MorphismType:
        """A morphism between finite cardinal objects."""

    def __call__(self, value: int) -> CardinalCategory.ObjectType:
        normalized = int(value)
        assert normalized == value and normalized >= 0
        return self.ObjectType(normalized)

    def zero(self) -> CardinalCategory.ObjectType:
        return self(0)

    def _equal_objects(
        self,
        first: CardinalCategory.ObjectType,
        second: CardinalCategory.ObjectType,
        assumptions: Proposition,
    ) -> bool | None:
        return first.value() == second.value()

    def __repr__(self) -> str:
        return "Cardinal"


_CARDINAL = CardinalCategory()


def Cardinal() -> CardinalCategory:
    """Return the owned category of represented finite cardinals."""
    return _CARDINAL


register_handler(_CARDINAL.equality(), _CARDINAL._equal_objects)
