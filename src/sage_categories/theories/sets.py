"""Sets and their category-owned operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache

from sage.rings.infinity import PlusInfinity
from sage.rings.integer import Integer
from sage.structure.element import Element

from sage_categories.category import Category
from sage_categories.functor import Functor
from sage_categories.theories.cardinals import (
    CardinalNumber,
    CardinalObject,
    Cardinals,
)
from sage_categories.values import (
    MathematicalElement,
    MathematicalMorphism,
    MathematicalObject,
)

type SetMember = (
    Element
    | MathematicalElement
    | MathematicalMorphism
    | MathematicalObject
    | int
    | str
)


class SetObject(MathematicalObject, ABC):
    """Base type for set implementations."""

    @abstractmethod
    def _cardinal_number(self) -> CardinalNumber:
        """Return the number used by the cardinality functor."""

    @abstractmethod
    def cardinality(self) -> CardinalObject:
        """Return this set's cardinality."""

    @abstractmethod
    def elements(self) -> tuple[SetMember, ...]:
        """Return the explicit finite carrier."""

    @abstractmethod
    def __contains__(self, value: SetMember) -> bool:
        """Test membership in the explicit finite carrier."""


@dataclass(frozen=True)
class Sets(Category):
    """The category of sets with a known cardinality."""

    class ObjectType(SetObject):
        """The implementation introduced by the category of sets."""

        def __init__(
            self,
            *,
            category: Sets,
            cardinal_number: CardinalNumber,
            elements: tuple[SetMember, ...] | None = None,
        ) -> None:
            super().__init__(category=category)
            self._number = cardinal_number
            self._elements = elements

        def _cardinal_number(self) -> CardinalNumber:
            return self._number

        def cardinality(self) -> CardinalObject:
            """Return this set's cardinality."""
            image = cardinality_functor()(self)
            if not isinstance(image, CardinalObject):
                raise TypeError("the cardinality functor returned a non-cardinal")
            return image

        def elements(self) -> tuple[SetMember, ...]:
            """Return the explicit finite carrier."""
            if self._elements is None:
                raise ValueError("this set has no explicit finite carrier")
            return self._elements

        def __contains__(self, value: SetMember) -> bool:
            if self._elements is None:
                raise ValueError("membership needs an explicit finite carrier")
            return value in self._elements

    def __call__(
        self,
        *,
        cardinal_number: CardinalNumber,
        elements: tuple[SetMember, ...] | None = None,
    ) -> SetObject:
        """Construct a set implementation."""
        return self.ObjectType(
            category=self,
            cardinal_number=cardinal_number,
            elements=elements,
        )


class CardinalityFunctor(Functor):
    """Map a set to its cardinality."""

    def __init__(self) -> None:
        super().__init__(Sets(), Cardinals())

    def on_object(self, source: MathematicalObject) -> MathematicalObject:
        if not isinstance(source, SetObject):
            raise TypeError("the cardinality functor expects a set")
        return Cardinals()(source._cardinal_number())

    def on_morphism(self, morphism: MathematicalMorphism) -> MathematicalMorphism:
        raise TypeError("cardinality does not map set functions to cardinal arrows")


@cache
def cardinality_functor() -> CardinalityFunctor:
    """Return the cardinality functor from sets to cardinals."""
    return CardinalityFunctor()


def FiniteSet(elements: tuple[SetMember, ...]) -> SetObject:
    """Construct a finite set from a duplicate-free carrier."""
    if len(set(elements)) != len(elements):
        raise ValueError("a finite-set carrier cannot contain duplicates")
    return Sets()(cardinal_number=Integer(len(elements)), elements=elements)


def SetWithCardinality(cardinality: CardinalNumber) -> SetObject:
    """Construct a set represented only by its cardinality."""
    if not isinstance(cardinality, Integer | PlusInfinity):
        raise TypeError("the supplied cardinality is not a cardinal number")
    return Sets()(cardinal_number=cardinality)
