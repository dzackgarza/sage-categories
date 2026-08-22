"""Descriptors installed on complete implementation classes."""

from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING

from sage_categories.values import MathematicalObject

if TYPE_CHECKING:
    from sage_categories.category import Category


class ForwardedAttribute:
    """Read a method from an object's cached functor image."""

    def __init__(self, owner: Category, name: str) -> None:
        self._owner = owner
        self._name = name

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner_type: type[MathematicalObject] | None = None,
    ) -> ForwardedAttribute | MethodType:
        if instance is None:
            return self
        implementation = instance.implementation_in(self._owner)
        method = getattr(implementation, self._name)
        if not isinstance(method, MethodType):
            raise TypeError(
                f"{self._owner!r}.{self._name} is not an instance method"
            )
        return method

