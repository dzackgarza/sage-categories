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
        *,
        element_method: bool,
    ) -> None:
        assert route
        self._route = route
        self._method = method
        self._element_method = element_method

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedMethod | MethodType:
        if instance is None:
            return self
        if self._element_method:
            image = instance._element_image_along(self._route)
        else:
            image = instance._object_image_along(self._route)
        return MethodType(self._method, image)
