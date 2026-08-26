"""Cardinal numbers and their thin category.

The symbolic representation follows the cardinal-expression design in
``dzack_research.preamble.categories.sets.cardinals``. It uses no Sage
category or Sage parent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeIs

from sage_categories.theories.cardinal_categories import (
    CardinalHomCategory,
    CardinalMorphism,
    Cardinals,
    CardinalsCategory,
    is_cardinal_hom_category,
)
from sage_categories.theories.cardinal_values import Cardinal, CardinalKind
from sage_categories.types import (
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.theories.ordinals import Ordinal


def is_cardinal(value: int | Cardinal) -> TypeIs[Cardinal]:
    represented = registered_value(value)
    return represented is not None and Cardinals().contains_cardinal(represented)


def cardinal(value: int | Cardinal) -> Cardinal:
    if is_cardinal(value):
        return value
    return Cardinals()(value)


def aleph(index: int | Ordinal) -> Cardinal:
    return Cardinals().aleph(index)


def Aleph0() -> Cardinal:
    return Cardinals().aleph(0)


def Continuum() -> Cardinal:
    return Cardinals().power(cardinal(2), Aleph0())


def SymbolicCardinal(name: str) -> Cardinal:
    return Cardinals().symbol(name)


aleph0 = Aleph0()
continuum = Continuum()
__all__ = (
    "Aleph0",
    "Cardinal",
    "CardinalHomCategory",
    "CardinalKind",
    "CardinalMorphism",
    "Cardinals",
    "CardinalsCategory",
    "Continuum",
    "SymbolicCardinal",
    "aleph",
    "cardinal",
    "is_cardinal",
    "is_cardinal_hom_category",
)
