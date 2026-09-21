"""Typed mathematical construction and choice owners over private kernel retention."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from sage_categories.kernel.retention import RetainedConstruction, RetainedSelection

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories

__all__ = ["ChosenConstruction", "SelectedChoice"]


class ChosenConstruction:
    """One mathematical construction whose result is retained on exact owned inputs."""

    def __init__(self) -> None:
        self._retained = RetainedConstruction()

    def __call__[Owner, Value](
        self,
        owner: Owner,
        parameters: tuple[object, ...],
        construct: Callable[[], Value],
    ) -> Value:
        return self._retained.value(owner, parameters, construct)


class SelectedChoice[Value]:
    """One mathematical choice family retained on exact owned inputs."""

    def __init__(self) -> None:
        self._retained: RetainedSelection[CategoryOfCategories.ElementType, Value] = RetainedSelection()

    def has(self, owner: CategoryOfCategories.ElementType, parameters: tuple[object, ...]) -> bool:
        return self._retained.has(owner, parameters)

    def select(
        self,
        owner: CategoryOfCategories.ElementType,
        parameters: tuple[object, ...],
        value: Value,
    ) -> None:
        self._retained.select(owner, parameters, value)

    def selected(self, owner: CategoryOfCategories.ElementType, parameters: tuple[object, ...]) -> Value:
        return self._retained.selected(owner, parameters)
