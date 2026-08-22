"""Cardinal values and their arithmetic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from sage.rings.infinity import PlusInfinity
from sage.rings.integer import Integer

from sage_categories.category import Category
from sage_categories.values import MathematicalObject

type CardinalNumber = Integer | PlusInfinity
type EqualityOperand = object


class CardinalObject(MathematicalObject, ABC):
    """Base type for cardinal implementations."""

    @abstractmethod
    def _cardinal_number(self) -> CardinalNumber:
        """Return the Sage number used for cardinal arithmetic."""


@dataclass(frozen=True)
class Cardinals(Category):
    """The category of cardinal values used by this framework."""

    class ObjectType(CardinalObject):
        """The implementation introduced by cardinal values."""

        def __init__(self, *, category: Cardinals, number: CardinalNumber) -> None:
            super().__init__(category=category)
            self._number = number

        def _cardinal_number(self) -> CardinalNumber:
            return self._number

        def __eq__(self, other: EqualityOperand) -> bool:
            if isinstance(other, CardinalObject):
                return self._number == other._cardinal_number()
            if not isinstance(other, int | Integer | PlusInfinity):
                return False
            return self._number == other

        def __int__(self) -> int:
            if not isinstance(self._number, Integer):
                raise TypeError("an infinite cardinal is not an integer")
            return int(self._number)

        def __mul__(self, other: CardinalObject) -> CardinalObject:
            candidate = self._number * other._cardinal_number()
            if not isinstance(candidate, Integer | PlusInfinity):
                raise TypeError("cardinal multiplication returned a non-cardinal value")
            return Cardinals()(candidate)

        def __repr__(self) -> str:
            return repr(self._number)

    def __call__(self, number: CardinalNumber | int) -> CardinalObject:
        """Construct a cardinal value."""
        normalized = Integer(number) if isinstance(number, int) else number
        if isinstance(normalized, Integer) and normalized < 0:
            raise ValueError("a cardinal cannot be negative")
        return self.ObjectType(category=self, number=normalized)
