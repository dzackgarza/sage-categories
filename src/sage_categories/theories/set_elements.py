"""The owned category of sets and functions.

This module migrates the mathematical ownership from
``dzack_research.preamble.categories.sets``. It uses only the owned
categorical foundation. Sage is not part of this category graph.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Self, TypeIs

import sage_categories

from sage_categories.abstract_categories.functors import (
    DiscreteObject,
)
from sage_categories.category import Category
from sage_categories.values import (
    Decision,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.theories.set_objects import SetObject
    from sage_categories.theories.set_subobjects import SetMorphism

type SetElementFamily = Callable[[SetElement], SetElement]
type MembershipPredicate = Callable[[SetElement], Decision]
type SetIterator = Callable[[], Iterator[SetElement]]


type SetMorphismFamily = Callable[[DiscreteObject], SetMorphism]


class SetElement(MathematicalElement):
    """An element of one owned set."""

    def __init__(
        self,
        *,
        category: Category,
        ambient_object: sage_categories.theories.set_objects.SetObject,
    ) -> None:
        from sage_categories.theories.set_category import Sets

        assert ambient_object in Sets()
        assert category is SetElements() or category.is_subcategory(SetElements())
        super().__init__(
            category=category,
            ambient_object=ambient_object,
        )

    def ambient_set(self) -> sage_categories.theories.set_objects.SetObject:
        from sage_categories.theories.set_category import Sets

        ambient = self.ambient_object()
        assert Sets().contains_set(ambient)
        return ambient

    def value(self) -> MathematicalObject:
        return self._value_()

    def _value_(self) -> MathematicalObject:
        return self


class SetElementsCategory(Category):
    """The total category of elements of owned sets."""

    ObjectType = SetElement

    def __init__(self) -> None:
        super().__init__()

    def contains_set_element(
        self,
        candidate: MathematicalObject,
    ) -> TypeIs[SetElement]:
        return candidate in self

    def __repr__(self) -> str:
        return "Elements of sets"


_SET_ELEMENTS: SetElementsCategory | None = None


def SetElements() -> SetElementsCategory:
    global _SET_ELEMENTS

    if _SET_ELEMENTS is None:
        _SET_ELEMENTS = SetElementsCategory()
    return _SET_ELEMENTS
