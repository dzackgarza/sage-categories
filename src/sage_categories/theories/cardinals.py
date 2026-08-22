"""Finite cardinal numbers used by the first set implementation."""

from __future__ import annotations

from typing import Any, TypeIs

from sage_categories.category import Category
from sage_categories.values import MathematicalObject


class FiniteCardinal(MathematicalObject):
    """A finite cardinal number."""

    def __init__(self, *, category: CardinalsCategory, number: int) -> None:
        assert number >= 0
        self._number = number
        super().__init__(category=category)

    def __eq__(self, other: Any) -> bool:
        if other is self:
            return True
        return self._number == other

    def __hash__(self) -> int:
        return hash(self._number)

    def __int__(self) -> int:
        return self._number

    def __add__(self, other: FiniteCardinal) -> FiniteCardinal:
        return Cardinals()(self._number + int(other))

    def __mul__(self, other: FiniteCardinal) -> FiniteCardinal:
        return Cardinals()(self._number * int(other))

    def __pow__(self, exponent: FiniteCardinal) -> FiniteCardinal:
        return Cardinals()(self._number ** int(exponent))

    def __repr__(self) -> str:
        return str(self._number)


class CardinalsCategory(Category):
    """The category containing the finite cardinal values used here."""

    ObjectType = FiniteCardinal

    def __init__(self) -> None:
        super().__init__(object_type=CardinalsCategory.ObjectType)

    def __call__(self, number: int) -> FiniteCardinal:
        result = self.ObjectType(category=self, number=number)
        assert self.contains_cardinal(result)
        return result

    def contains_cardinal(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[FiniteCardinal]:
        return candidate in self

    def __repr__(self) -> str:
        return "Card"


_CARDINALS = CardinalsCategory()


def Cardinals() -> CardinalsCategory:
    """Return the category of represented cardinal values."""
    return _CARDINALS
