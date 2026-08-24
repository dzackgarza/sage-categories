"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from enum import Enum
from typing import TYPE_CHECKING, Any

from sage_categories.values import (
    Arrow,
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


type MethodCallable = Callable[..., Any]


def _forward_argument(
    argument: Any,
    route: tuple[StructuralFunctor, ...],
    context: MathematicalObject | MathematicalElement | Arrow,
) -> Any:
    """Forward a method argument along a structural-functor route."""
    if isinstance(context, MathematicalObject):
        if (element := registered_element(argument)) is not None:
            if element.ambient_object() is context or element.ambient_object().category() is context.category():
                return element._element_image_along(route)
        elif (val := registered_value(argument)) is not None and val.category() is context.category():
            return val._object_image_along(route)
        elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is context.category():
            return arr._morphism_image_along(route)
    elif isinstance(context, MathematicalElement):
        source_ambient = context.ambient_object()
        if (element := registered_element(argument)) is not None:
            if element.ambient_object() is source_ambient or element.ambient_object().category() is source_ambient.category():
                return element._element_image_along(route)
        elif (val := registered_value(argument)) is not None and val.category() is source_ambient.category():
            return val._object_image_along(route)
        elif (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_ambient.category():
            return arr._morphism_image_along(route)
    elif isinstance(context, Arrow):
        source_category = context.base_category()
        if (arr := registered_value(argument)) is not None and isinstance(arr, Arrow) and arr.base_category() is source_category:
            return arr._morphism_image_along(route)
        elif (element := registered_element(argument)) is not None:
            if element.ambient_object() is context.domain() or element.ambient_object().category() is source_category:
                return element._element_image_along(route)
        elif (val := registered_value(argument)) is not None and val.category() is source_category:
            return val._object_image_along(route)
    return argument


def _transport_args(
    args: tuple[Any, ...],
    route: tuple[StructuralFunctor, ...],
    context: MathematicalObject | MathematicalElement | Arrow,
) -> tuple[Any, ...]:
    return tuple(_forward_argument(arg, route, context) for arg in args)


def _transport_kwargs(
    kwargs: dict[str, Any],
    route: tuple[StructuralFunctor, ...],
    context: MathematicalObject | MathematicalElement | Arrow,
) -> dict[str, Any]:
    return {k: _forward_argument(v, route, context) for k, v in kwargs.items()}


def _transport_result(
    result: Any,
    route: tuple[StructuralFunctor, ...],
    context: MathematicalObject | MathematicalElement | Arrow,
    image_context: MathematicalObject | MathematicalElement | Arrow,
) -> Any:
    """Transport a method result value back through the reverse structural route."""
    if result is image_context:
        return context

    if isinstance(context, MathematicalObject):
        target_element = registered_element(result)
        if target_element is not None and target_element.ambient_object() is image_context:
            objects: list[MathematicalObject] = [context]
            prefix: tuple[StructuralFunctor, ...] = ()
            for functor in route[:-1]:
                prefix = (*prefix, functor)
                objects.append(context._object_image_along(prefix))
            element = target_element
            for functor, source_object in reversed(tuple(zip(route, objects, strict=True))):
                element = functor.preimage_element(source_object, element)
            return element
    elif isinstance(context, MathematicalElement):
        source_ambient = context.ambient_object()
        assert isinstance(image_context, MathematicalElement)
        target_ambient = image_context.ambient_object()
        if result is target_ambient:
            return source_ambient
        target_element = registered_element(result)
        if target_element is not None and target_element.ambient_object() is target_ambient:
            objects = [source_ambient]
            prefix = ()
            for functor in route[:-1]:
                prefix = (*prefix, functor)
                objects.append(source_ambient._object_image_along(prefix))
            element = target_element
            for functor, source_object in reversed(tuple(zip(route, objects, strict=True))):
                element = functor.preimage_element(source_object, element)
            return element
    elif isinstance(context, Arrow):
        source_codomain = context.codomain()
        assert isinstance(image_context, Arrow)
        target_codomain = image_context.codomain()
        if result is target_codomain:
            return source_codomain
        target_element = registered_element(result)
        if target_element is not None and target_element.ambient_object() is target_codomain:
            objects = [source_codomain]
            prefix = ()
            for functor in route[:-1]:
                prefix = (*prefix, functor)
                objects.append(source_codomain._object_image_along(prefix))
            element = target_element
            for functor, source_object in reversed(tuple(zip(route, objects, strict=True))):
                element = functor.preimage_element(source_object, element)
            return element

    if isinstance(result, Iterator) or (
        isinstance(result, Iterable) and not isinstance(result, (str, bytes, MathematicalObject, MathematicalElement, Arrow, dict, tuple))
    ):

        def lazy_results() -> Iterator[Any]:
            for item in result:
                yield _transport_result(item, route, context, image_context)

        return lazy_results()

    return result


class ForwardedObjectMethod:
    """Forward an object method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: MethodCallable,
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: MathematicalObject | None,
        owner: type[MathematicalObject] | None = None,
    ) -> ForwardedObjectMethod | MethodCallable:
        if instance is None:
            return self

        image = instance._object_image_along(self._route)

        def call(*args: Any, **kwargs: Any) -> Any:
            forwarded_args = _transport_args(args, self._route, instance)
            forwarded_kwargs = _transport_kwargs(kwargs, self._route, instance)
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(result, self._route, instance, image)

        return call


class ForwardedElementMethod:
    """Forward an element method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: MethodCallable,
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: MathematicalElement | None,
        owner: type[MathematicalElement] | None = None,
    ) -> ForwardedElementMethod | MethodCallable:
        if instance is None:
            return self

        image = instance._element_image_along(self._route)

        def call_element(*args: Any, **kwargs: Any) -> Any:
            forwarded_args = _transport_args(args, self._route, instance)
            forwarded_kwargs = _transport_kwargs(kwargs, self._route, instance)
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(result, self._route, instance, image)

        return call_element


class ForwardedArrowMethod:
    """Forward an arrow method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: MethodCallable,
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Arrow | None,
        owner: type[Arrow] | None = None,
    ) -> ForwardedArrowMethod | MethodCallable:
        if instance is None:
            return self

        image = instance._morphism_image_along(self._route)

        def call_arrow(*args: Any, **kwargs: Any) -> Any:
            forwarded_args = _transport_args(args, self._route, instance)
            forwarded_kwargs = _transport_kwargs(kwargs, self._route, instance)
            result = self._method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(result, self._route, instance, image)

        return call_arrow


type ForwardedDescriptor = (
    ForwardedObjectMethod
    | ForwardedElementMethod
    | ForwardedArrowMethod
)
