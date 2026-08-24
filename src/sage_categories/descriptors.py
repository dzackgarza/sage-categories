"""Descriptors for functorial method inheritance."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from enum import Enum
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar, cast

from sage_categories.values import (
    Arrow,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor


class ImplementationRole(Enum):
    """The mathematical role of a compiled implementation method."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


P = ParamSpec("P")
R = TypeVar("R")


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


def _forward_arg(
    arg: object,
    route: tuple[StructuralFunctor, ...],
) -> object:
    if not route:
        return arg
    source_cat = route[0].domain()
    if isinstance(arg, MathematicalElement):
        ambient = arg.ambient_object()
        if ambient in source_cat or ambient.category() is source_cat:
            return arg._element_image_along(route)
        return arg
    if isinstance(arg, MathematicalObject):
        if arg in source_cat or arg.category() is source_cat:
            return arg._object_image_along(route)
        return arg
    if isinstance(arg, Arrow):
        if arg.domain() in source_cat and arg.codomain() in source_cat:
            return arg._morphism_image_along(route)
        return arg
    return arg


def _forward_args(
    args: tuple[object, ...],
    route: tuple[StructuralFunctor, ...],
) -> tuple[object, ...]:
    return tuple(_forward_arg(arg, route) for arg in args)


def _forward_kwargs(
    kwargs: dict[str, object],
    route: tuple[StructuralFunctor, ...],
) -> dict[str, object]:
    return {name: _forward_arg(val, route) for name, val in kwargs.items()}


def _transport_result[ResultType](
    result: ResultType,
    route: tuple[StructuralFunctor, ...],
    source_ambient: MathematicalObject,
    target_ambient: MathematicalObject | None = None,
    instance: MathematicalObject | MathematicalElement | Arrow | None = None,
    image: MathematicalObject | MathematicalElement | Arrow | None = None,
) -> ResultType:
    if result is None:
        return result
    if image is not None and result is image:
        assert instance is not None
        return cast(ResultType, instance)
    if target_ambient is not None and result is target_ambient:
        return cast(ResultType, source_ambient)

    if isinstance(result, Iterator):

        def lazy_elements() -> Iterator[object]:
            for item in result:
                if isinstance(item, MathematicalElement):
                    yield _pull_back_element_along(item, route, source_ambient)
                else:
                    yield item

        return cast(ResultType, lazy_elements())

    if isinstance(result, MathematicalElement):
        if target_ambient is not None and result.ambient_object() is target_ambient:
            return cast(ResultType, _pull_back_element_along(result, route, source_ambient))
        return result

    if isinstance(result, MathematicalObject):
        if target_ambient is not None and result is target_ambient:
            return cast(ResultType, source_ambient)
        return result

    return result


class ForwardedObjectMethod[Receiver: MathematicalObject, **P, R]:
    """Forward an object method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[MathematicalObject, P], R],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedObjectMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self

        image = instance._object_image_along(self._route)

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args = _forward_args(args, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._route)
            raw_method = cast(Callable[..., R], self._method)
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(
                result,
                self._route,
                source_ambient=instance,
                target_ambient=image,
                instance=instance,
                image=image,
            )

        return call


class ForwardedElementMethod[Receiver: MathematicalElement, **P, R]:
    """Forward an element method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[MathematicalElement, P], R],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedElementMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self

        image = instance._element_image_along(self._route)
        source_ambient = instance.ambient_object()

        def call_element(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args = _forward_args(args, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._route)
            raw_method = cast(Callable[..., R], self._method)
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(
                result,
                self._route,
                source_ambient=source_ambient,
                target_ambient=image.ambient_object(),
                instance=instance,
                image=image,
            )

        return call_element


class ForwardedArrowMethod[Receiver: Arrow, **P, R]:
    """Forward an arrow method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[Arrow, P], R],
    ) -> None:
        assert route
        self._route = route
        self._method = method

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedArrowMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self

        image = instance._morphism_image_along(self._route)

        def call_arrow(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args = _forward_args(args, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._route)
            raw_method = cast(Callable[..., R], self._method)
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            return _transport_result(
                result,
                self._route,
                source_ambient=instance.codomain(),
                target_ambient=image.codomain(),
                instance=instance,
                image=image,
            )

        return call_arrow


type ForwardedDescriptor = (
    ForwardedObjectMethod[MathematicalObject, ..., object] | ForwardedElementMethod[MathematicalElement, ..., object] | ForwardedArrowMethod[Arrow, ..., object]
)
