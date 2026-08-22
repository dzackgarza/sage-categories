"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
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
        morphism_method: bool,
    ) -> None:
        assert route
        assert not (element_method and morphism_method)
        self._route = route
        self._method = method
        self._element_method = element_method
        self._morphism_method = morphism_method

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedMethod | MethodType:
        if instance is None:
            return self
        image: MathematicalObject
        if self._morphism_method:
            image = instance._morphism_image_along(self._route)
        elif self._element_method:
            image = instance._element_image_along(self._route)
        else:
            image = instance._object_image_along(self._route)
        implementation = next(
            candidate
            for implementation_type in image.__class__.__mro__
            if (
                candidate := implementation_type.__dict__.get(
                    self._method.__name__
                )
            )
            is not None
            and inspect.isfunction(candidate)
        )
        return MethodType(implementation, image)
