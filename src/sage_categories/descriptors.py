"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from enum import Enum
from typing import TYPE_CHECKING

from sage_categories.values import (
    Arrow,
    Decision,
    MathematicalElement,
    MathematicalObject,
    registered_element,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor


class ImplementationRole(Enum):
    """The mathematical role of a compiled implementation method."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


type MathematicalValue = MathematicalObject | MathematicalElement | Arrow

type TransportableValue = MathematicalValue | Decision | int | str | None | Iterator[MathematicalElement] | Iterator[MathematicalObject] | Iterator[Arrow]


def _pull_back_element_along(
    element: MathematicalElement,
    route: tuple[StructuralFunctor, ...],
    source_ambient: MathematicalObject,
) -> MathematicalElement:
    objects: list[MathematicalObject] = [source_ambient]
    prefix: tuple[StructuralFunctor, ...] = ()
    for functor in route[:-1]:
        prefix = (*prefix, functor)
        objects.append(source_ambient._object_image_along(prefix))
    current = element
    for functor, src in reversed(tuple(zip(route, objects, strict=True))):
        current = functor.preimage_element(src, current)
    return current


def _forward_object_argument(
    argument: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: MathematicalObject,
) -> TransportableValue:
    if (element := registered_element(argument)) is not None:
        if element.ambient_object() is instance or element.ambient_object().category() is instance.category():
            return element._element_image_along(route)
    elif (val := registered_value(argument)) is not None and val.category() is instance.category():
        return val._object_image_along(route)
    elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is instance.category():
        return arr._morphism_image_along(route)
    return argument


def _transport_object_result(
    result: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: MathematicalObject,
    image: MathematicalObject,
) -> TransportableValue:
    if result is image:
        return instance
    target_element = registered_element(result)
    if target_element is not None and target_element.ambient_object() is image:
        return _pull_back_element_along(target_element, route, instance)
    if isinstance(result, Iterator) or (isinstance(result, Iterable) and not isinstance(result, (str, bytes, MathematicalObject, MathematicalElement, Arrow, dict, tuple))):

        def lazy_results() -> Iterator[MathematicalElement]:
            for item in result:
                transported = _transport_object_result(item, route, instance, image)
                assert isinstance(transported, MathematicalElement)
                yield transported

        return lazy_results()
    return result


class ForwardedObjectMethod[Receiver: MathematicalObject]:
    """Forward an object method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., TransportableValue],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedObjectMethod[Receiver] | Callable[..., TransportableValue]:
        if instance is None:
            return self

        image = instance._object_image_along(self._route)

        def call(*args: TransportableValue, **kwargs: TransportableValue) -> TransportableValue:
            forwarded_args = tuple(_forward_object_argument(arg, self._route, instance) for arg in args)
            forwarded_kwargs = {k: _forward_object_argument(v, self._route, instance) for k, v in kwargs.items()}
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_object_result(result, self._route, instance, image)

        return call


def _forward_element_argument(
    argument: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: MathematicalElement,
) -> TransportableValue:
    source_ambient = instance.ambient_object()
    if (element := registered_element(argument)) is not None:
        if element.ambient_object() is source_ambient or element.ambient_object().category() is source_ambient.category():
            return element._element_image_along(route)
    elif (val := registered_value(argument)) is not None and val.category() is source_ambient.category():
        return val._object_image_along(route)
    elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_ambient.category():
        return arr._morphism_image_along(route)
    return argument


def _transport_element_result(
    result: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: MathematicalElement,
    image: MathematicalElement,
) -> TransportableValue:
    source_ambient = instance.ambient_object()
    target_ambient = image.ambient_object()
    if result is target_ambient:
        return source_ambient
    if result is image:
        return instance
    target_element = registered_element(result)
    if target_element is not None and target_element.ambient_object() is target_ambient:
        return _pull_back_element_along(target_element, route, source_ambient)
    if isinstance(result, Iterator) or (isinstance(result, Iterable) and not isinstance(result, (str, bytes, MathematicalObject, MathematicalElement, Arrow, dict, tuple))):

        def lazy_results() -> Iterator[MathematicalElement]:
            for item in result:
                transported = _transport_element_result(item, route, instance, image)
                assert isinstance(transported, MathematicalElement)
                yield transported

        return lazy_results()
    return result


class ForwardedElementMethod[Receiver: MathematicalElement]:
    """Forward an element method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., TransportableValue],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedElementMethod[Receiver] | Callable[..., TransportableValue]:
        if instance is None:
            return self

        image = instance._element_image_along(self._route)

        def call_element(*args: TransportableValue, **kwargs: TransportableValue) -> TransportableValue:
            forwarded_args = tuple(_forward_element_argument(arg, self._route, instance) for arg in args)
            forwarded_kwargs = {k: _forward_element_argument(v, self._route, instance) for k, v in kwargs.items()}
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_element_result(result, self._route, instance, image)

        return call_element


def _forward_arrow_argument(
    argument: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: Arrow,
) -> TransportableValue:
    source_category = instance.base_category()
    if (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_category:
        return arr._morphism_image_along(route)
    elif (element := registered_element(argument)) is not None:
        if element.ambient_object() is instance.domain() or element.ambient_object().category() is source_category:
            return element._element_image_along(route)
    elif (val := registered_value(argument)) is not None and val.category() is source_category:
        return val._object_image_along(route)
    return argument


def _transport_arrow_result(
    result: TransportableValue,
    route: tuple[StructuralFunctor, ...],
    instance: Arrow,
    image: Arrow,
) -> TransportableValue:
    source_codomain = instance.codomain()
    target_codomain = image.codomain()
    if result is image:
        return instance
    if result is target_codomain:
        return source_codomain
    target_element = registered_element(result)
    if target_element is not None and target_element.ambient_object() is target_codomain:
        return _pull_back_element_along(target_element, route, source_codomain)
    if isinstance(result, Iterator) or (isinstance(result, Iterable) and not isinstance(result, (str, bytes, MathematicalObject, MathematicalElement, Arrow, dict, tuple))):

        def lazy_results() -> Iterator[MathematicalElement]:
            for item in result:
                transported = _transport_arrow_result(item, route, instance, image)
                assert isinstance(transported, MathematicalElement)
                yield transported

        return lazy_results()
    return result


class ForwardedArrowMethod[Receiver: Arrow]:
    """Forward an arrow method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[..., TransportableValue],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedArrowMethod[Receiver] | Callable[..., TransportableValue]:
        if instance is None:
            return self

        image = instance._morphism_image_along(self._route)

        def call_arrow(*args: TransportableValue, **kwargs: TransportableValue) -> TransportableValue:
            forwarded_args = tuple(_forward_arrow_argument(arg, self._route, instance) for arg in args)
            forwarded_kwargs = {k: _forward_arrow_argument(v, self._route, instance) for k, v in kwargs.items()}
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_arrow_result(result, self._route, instance, image)

        return call_arrow


type ForwardedDescriptor = ForwardedObjectMethod[MathematicalObject] | ForwardedElementMethod[MathematicalElement] | ForwardedArrowMethod[Arrow]
