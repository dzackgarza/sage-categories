"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from enum import Enum
from typing import TYPE_CHECKING

from sage_categories.values import Arrow, MathematicalElement, MathematicalObject

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor


class ImplementationRole(Enum):
    """The mathematical role of a compiled implementation method."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


class ForwardedObjectMethod:
    """Forward an object method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., object],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedObjectMethod | Callable[..., object]:
        if instance is None:
            return self

        image = instance._object_image_along(self._route)

        if self._method.__name__ == "__contains__":

            def contains(candidate: object) -> bool:
                from sage_categories.values import registered_element

                source_element = registered_element(candidate)
                if source_element is None or source_element.ambient_object() is not instance:
                    return False
                target = source_element._element_image_along(self._route)
                return bool(self._method(image, target))

            return contains

        if self._method.__name__ == "__iter__":

            def iterate() -> Iterator[MathematicalElement]:
                from sage_categories.values import registered_element

                target_raw = self._method(image)
                assert isinstance(target_raw, Iterable)
                target_elements: Iterable[object] = target_raw
                objects: list[MathematicalObject] = [instance]
                prefix: tuple[StructuralFunctor, ...] = ()
                for functor in self._route[:-1]:
                    prefix = (*prefix, functor)
                    objects.append(instance._object_image_along(prefix))
                route_and_objects = tuple(zip(self._route, objects, strict=True))
                for target in target_elements:
                    target_element = registered_element(target)
                    assert target_element is not None
                    element = target_element
                    for functor, source_object in reversed(route_and_objects):
                        element = functor.preimage_element(source_object, element)
                    yield element

            return iterate

        def call(*args: object, **kwargs: object) -> object:
            from sage_categories.values import (
                registered_element,
                registered_value,
            )

            forwarded_args: list[object] = []
            for argument in args:
                if (element := registered_element(argument)) is not None and element.ambient_object() is instance:
                    forwarded_args.append(element._element_image_along(self._route))
                elif (val := registered_value(argument)) is not None and val.category() is instance.category():
                    forwarded_args.append(val._object_image_along(self._route))
                elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is instance.category():
                    forwarded_args.append(arr._morphism_image_along(self._route))
                else:
                    forwarded_args.append(argument)

            result = self._method(image, *forwarded_args, **kwargs)

            if result is image:
                return instance
            target_element = registered_element(result)
            if target_element is not None and target_element.ambient_object() is image:
                objects: list[MathematicalObject] = [instance]
                prefix: tuple[StructuralFunctor, ...] = ()
                for functor in self._route[:-1]:
                    prefix = (*prefix, functor)
                    objects.append(instance._object_image_along(prefix))
                element = target_element
                for functor, source_object in reversed(tuple(zip(self._route, objects, strict=True))):
                    element = functor.preimage_element(source_object, element)
                return element
            return result

        return call


class ForwardedElementMethod:
    """Forward an element method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., object],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: MathematicalElement | None,
        owner: type[MathematicalElement] | None = None,
    ) -> ForwardedElementMethod | Callable[..., object]:
        if instance is None:
            return self

        source_ambient = instance.ambient_object()
        image = instance._element_image_along(self._route)
        target_ambient = image.ambient_object()

        def call_element(*args: object, **kwargs: object) -> object:
            from sage_categories.values import (
                registered_element,
                registered_value,
            )

            forwarded_args: list[object] = []
            for argument in args:
                if (element := registered_element(argument)) is not None and element.ambient_object() is source_ambient:
                    forwarded_args.append(element._element_image_along(self._route))
                elif (val := registered_value(argument)) is not None and val.category() is source_ambient.category():
                    forwarded_args.append(val._object_image_along(self._route))
                elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_ambient.category():
                    forwarded_args.append(arr._morphism_image_along(self._route))
                else:
                    forwarded_args.append(argument)

            result = self._method(image, *forwarded_args, **kwargs)

            if result is target_ambient:
                return source_ambient
            if result is image:
                return instance
            target_element = registered_element(result)
            if target_element is not None and target_element.ambient_object() is target_ambient:
                objects: list[MathematicalObject] = [source_ambient]
                prefix: tuple[StructuralFunctor, ...] = ()
                for functor in self._route[:-1]:
                    prefix = (*prefix, functor)
                    objects.append(source_ambient._object_image_along(prefix))
                element = target_element
                for functor, source_object in reversed(tuple(zip(self._route, objects, strict=True))):
                    element = functor.preimage_element(source_object, element)
                return element
            return result

        return call_element


class ForwardedArrowMethod:
    """Forward an arrow method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., object],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Arrow | None,
        owner: type[Arrow] | None = None,
    ) -> ForwardedArrowMethod | Callable[..., object]:
        if instance is None:
            return self

        image = instance._morphism_image_along(self._route)
        source_category = instance.base_category()

        def call_arrow(*args: object, **kwargs: object) -> object:
            from sage_categories.values import (
                registered_element,
                registered_value,
            )

            forwarded_args: list[object] = []
            for argument in args:
                if (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_category:
                    forwarded_args.append(arr._morphism_image_along(self._route))
                elif (element := registered_element(argument)) is not None and element.ambient_object() is instance.domain():
                    forwarded_args.append(element._element_image_along(self._route))
                elif (val := registered_value(argument)) is not None and val.category() is source_category:
                    forwarded_args.append(val._object_image_along(self._route))
                else:
                    forwarded_args.append(argument)

            result = self._method(image, *forwarded_args, **kwargs)

            if result is image:
                return instance
            return result

        return call_arrow


type ForwardedDescriptor = ForwardedObjectMethod | ForwardedElementMethod | ForwardedArrowMethod
