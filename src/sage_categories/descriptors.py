"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from enum import Enum
from types import FunctionType, MethodType
from typing import TYPE_CHECKING, Any, assert_never

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
    ) -> ForwardedMethod | MethodType | Callable[..., Any]:
        if instance is None:
            return self
        step: tuple[StructuralFunctor, ...] = (self._route[0],)
        image: MathematicalObject
        match self._role:
            case ImplementationRole.OBJECT:
                image = instance._object_image_along(step)
            case ImplementationRole.ELEMENT:
                image = instance._element_image_along(step)
            case ImplementationRole.ARROW:
                image = instance._morphism_image_along(step)
            case _:
                assert_never(self._role)
        while image is instance and len(step) < len(self._route):
            step = self._route[: len(step) + 1]
            match self._role:
                case ImplementationRole.OBJECT:
                    image = instance._object_image_along(step)
                case ImplementationRole.ELEMENT:
                    image = instance._element_image_along(step)
                case ImplementationRole.ARROW:
                    image = instance._morphism_image_along(step)
                case _:
                    assert_never(self._role)
        if (
            self._role is ImplementationRole.OBJECT
            and self._method.__name__ == "__contains__"
        ):

            def contains(candidate: Any) -> bool:
                from sage_categories.values import registered_element

                source_element = registered_element(candidate)
                if (
                    source_element is None
                    or source_element.ambient_object() is not instance
                ):
                    return False
                target = source_element._element_image_along(step)
                if image is instance:
                    return bool(self._method(image, target))
                return bool(self._method(image, target))

            return contains
        if (
            self._role is ImplementationRole.OBJECT
            and self._method.__name__ == "__iter__"
        ):

            def iterate() -> Iterator[MathematicalObject]:
                if image is instance:
                    targets: Iterator[MathematicalObject] = self._method(image)
                else:
                    declaration = inspect.getattr_static(
                        type(image), self._method.__name__
                    )
                    target_method = declaration.__get__(image, type(image))
                    targets = target_method()
                for target in targets:
                    from sage_categories.values import registered_element

                    target_element = registered_element(target)
                    assert target_element is target
                    source = instance
                    objects: list[MathematicalObject] = [source]
                    for functor in step[:-1]:
                        source = functor.on_object(source)
                        objects.append(source)
                    element = target_element
                    for functor, source_object in reversed(
                        tuple(zip(step, objects, strict=True))
                    ):
                        element = functor.preimage_element(source_object, element)
                    yield element

            return iterate
        if self._role is ImplementationRole.OBJECT:

            def call(*args: Any, **kwargs: Any) -> Any:
                from sage_categories.values import registered_element

                if image is instance:
                    target_method = MethodType(self._method, image)
                else:
                    declaration = inspect.getattr_static(
                        type(image), self._method.__name__
                    )
                    target_method = declaration.__get__(image, type(image))

                forwarded_args = tuple(
                    argument._element_image_along(step)
                    if (element := registered_element(argument)) is not None
                    and element.ambient_object() is instance
                    else argument
                    for argument in args
                )
                result = target_method(*forwarded_args, **kwargs)
                target_element = registered_element(result)
                if (
                    target_element is None
                    or target_element.ambient_object() is not image
                ):
                    return result
                source = instance
                objects: list[MathematicalObject] = [source]
                for functor in step[:-1]:
                    source = functor.on_object(source)
                    objects.append(source)
                element = target_element
                for functor, source_object in reversed(
                    tuple(zip(step, objects, strict=True))
                ):
                    element = functor.preimage_element(source_object, element)
                return element

            return call
        if self._role is ImplementationRole.ELEMENT:

            def call_element(*args: Any, **kwargs: Any) -> Any:
                from sage_categories.values import registered_element

                if image is instance:
                    target_method = MethodType(self._method, image)
                else:
                    declaration = inspect.getattr_static(
                        type(image), self._method.__name__
                    )
                    target_method = declaration.__get__(image, type(image))

                source_element = registered_element(instance)
                target_element = registered_element(image)
                assert source_element is instance
                assert target_element is image
                source_ambient = source_element.ambient_object()
                forwarded_args = tuple(
                    argument._element_image_along(step)
                    if (element := registered_element(argument)) is not None
                    and element.ambient_object() is source_ambient
                    else argument
                    for argument in args
                )
                result = target_method(*forwarded_args, **kwargs)
                if result is target_element.ambient_object():
                    return source_ambient
                return result

            return call_element
        return MethodType(self._method, image)
