"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from types import FunctionType, MethodType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.values import MathematicalObject


class ForwardedMethod:
    """Bind a category-owned method to an object's structural-functor image."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: FunctionType,
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedMethod | MethodType:
        if instance is None:
            return self
        image = instance._image_along(self._route)
        bound: MethodType = image.__getattribute__(self._method.__name__)
        return bound
