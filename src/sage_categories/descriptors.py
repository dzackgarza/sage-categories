"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from enum import Enum
from types import FunctionType, MethodType
from typing import TYPE_CHECKING, assert_never

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor
    from sage_categories.values import MathematicalObject


class ImplementationRole(Enum):
    """The mathematical role of a compiled implementation method."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


class ForwardedMethod:
    """Bind a category-owned method to an object's structural-functor image."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: FunctionType,
        *,
        role: ImplementationRole,
    ) -> None:
        assert route
        self._route = route
        self._method = method
        self._role = role

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedMethod | MethodType:
        if instance is None:
            return self
        image: MathematicalObject
        match self._role:
            case ImplementationRole.OBJECT:
                image = instance._object_image_along(self._route)
            case ImplementationRole.ELEMENT:
                image = instance._element_image_along(self._route)
            case ImplementationRole.ARROW:
                image = instance._morphism_image_along(self._route)
            case _:
                assert_never(self._role)
        return MethodType(self._method, image)
