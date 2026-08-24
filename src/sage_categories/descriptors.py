"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from enum import Enum
from types import UnionType
from typing import TYPE_CHECKING, Any, Concatenate, ParamSpec, TypeVar, get_args, get_origin

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


def _role_from_annotation(annotation: object) -> str:
    if annotation is inspect.Parameter.empty:
        return "value"
    if isinstance(annotation, str):
        ann_str = annotation.strip()
        if ann_str.startswith(("Iterator[", "Iterable[", "collections.abc.Iterator[", "collections.abc.Iterable[")):
            inner = ann_str[ann_str.index("[") + 1 : ann_str.rindex("]")]
            inner_role = _role_from_annotation(inner)
            return f"iterator_{inner_role}"
        if "Arrow" in ann_str or "Morphism" in ann_str:
            return "arrow"
        if "Element" in ann_str:
            return "element"
        if "Object" in ann_str or "Category" in ann_str or "Set" in ann_str or "Poset" in ann_str:
            return "object"
        return "value"

    origin = get_origin(annotation)
    if origin is not None:
        if isinstance(origin, type) and issubclass(origin, (Iterator,)):
            args = get_args(annotation)
            if args:
                return f"iterator_{_role_from_annotation(args[0])}"
            return "iterator_value"
        filtered_args = [a for a in get_args(annotation) if a is not type(None)]
        if filtered_args:
            return _role_from_annotation(filtered_args[0])
        return "value"

    if isinstance(annotation, type):
        if issubclass(annotation, Arrow):
            return "arrow"
        if issubclass(annotation, MathematicalElement):
            return "element"
        if issubclass(annotation, MathematicalObject):
            return "object"

    return "value"


def _inspect_method_roles(
    method: Callable[..., object],
) -> tuple[tuple[tuple[str, str], ...], str | None, str | None, str]:
    sig = inspect.signature(method)
    params = list(sig.parameters.values())[1:]
    roles_accumulator: list[tuple[str, str]] = []
    var_pos_role: str | None = None
    var_kw_role: str | None = None
    for p in params:
        role = _role_from_annotation(p.annotation)
        if p.kind == inspect.Parameter.VAR_POSITIONAL:
            var_pos_role = role
        elif p.kind == inspect.Parameter.VAR_KEYWORD:
            var_kw_role = role
        else:
            roles_accumulator.append((p.name, role))
    return_role = _role_from_annotation(sig.return_annotation)
    return tuple(roles_accumulator), var_pos_role, var_kw_role, return_role


def _forward_arg_by_role(
    arg: Any,
    role: str,
    route: tuple[StructuralFunctor, ...],
) -> Any:
    if arg is None:
        return arg
    if isinstance(arg, Arrow):
        return arg._morphism_image_along(route)
    if isinstance(arg, MathematicalElement):
        return arg._element_image_along(route)
    if isinstance(arg, MathematicalObject):
        return arg._object_image_along(route)
    return arg


def _forward_args(
    args: tuple[object, ...],
    param_roles: tuple[tuple[str, str], ...],
    var_pos_role: str | None,
    route: tuple[StructuralFunctor, ...],
) -> tuple[object, ...]:
    forwarded: list[object] = []
    num_positional = len(param_roles)
    for i, arg in enumerate(args):
        if i < num_positional:
            role = param_roles[i][1]
        elif var_pos_role is not None:
            role = var_pos_role
        else:
            role = "value"
        forwarded.append(_forward_arg_by_role(arg, role, route))
    return tuple(forwarded)


def _forward_kwargs(
    kwargs: dict[str, object],
    param_roles: tuple[tuple[str, str], ...],
    var_kw_role: str | None,
    route: tuple[StructuralFunctor, ...],
) -> dict[str, object]:
    roles_by_name = dict(param_roles)
    forwarded: dict[str, object] = {}
    for name, val in kwargs.items():
        role = roles_by_name[name] if name in roles_by_name else (var_kw_role if var_kw_role is not None else "value")
        forwarded[name] = _forward_arg_by_role(val, role, route)
    return forwarded


def _transport_result(
    result: Any,
    return_role: str,
    route: tuple[StructuralFunctor, ...],
    source_ambient: MathematicalObject,
    target_ambient: MathematicalObject | None = None,
    instance: MathematicalObject | None = None,
    image: MathematicalObject | None = None,
) -> Any:
    if result is None:
        return result
    if image is not None and result is image:
        assert instance is not None
        return instance
    if target_ambient is not None and result is target_ambient:
        return source_ambient

    if return_role == "iterator_element" or isinstance(result, Iterator):
        if isinstance(result, Iterator):
            def lazy_elements() -> Iterator[Any]:
                for item in result:
                    if isinstance(item, MathematicalElement):
                        yield _pull_back_element_along(item, route, source_ambient)
                    else:
                        yield item
            return lazy_elements()

    if isinstance(result, MathematicalElement):
        return _pull_back_element_along(result, route, source_ambient)

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
        self._param_roles, self._var_pos_role, self._var_kw_role, self._return_role = _inspect_method_roles(method)

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedObjectMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self

        image = instance._object_image_along(self._route)

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args = _forward_args(args, self._param_roles, self._var_pos_role, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._param_roles, self._var_kw_role, self._route)
            raw_method: Callable[..., Any] = self._method
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            transported: R = _transport_result(result, self._return_role, self._route, instance, image, instance=instance, image=image)
            return transported

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
        self._param_roles, self._var_pos_role, self._var_kw_role, self._return_role = _inspect_method_roles(method)

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
            forwarded_args = _forward_args(args, self._param_roles, self._var_pos_role, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._param_roles, self._var_kw_role, self._route)
            raw_method: Callable[..., Any] = self._method
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            transported: R = _transport_result(result, self._return_role, self._route, source_ambient, image.ambient_object(), instance=instance, image=image)
            return transported

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
        self._param_roles, self._var_pos_role, self._var_kw_role, self._return_role = _inspect_method_roles(method)

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedArrowMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self

        image = instance._morphism_image_along(self._route)

        def call_arrow(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args = _forward_args(args, self._param_roles, self._var_pos_role, self._route)
            forwarded_kwargs = _forward_kwargs(kwargs, self._param_roles, self._var_kw_role, self._route)
            raw_method: Callable[..., Any] = self._method
            result = raw_method(image, *forwarded_args, **forwarded_kwargs)
            transported: R = _transport_result(result, self._return_role, self._route, instance.codomain(), image.codomain(), instance=instance, image=image)
            return transported

        return call_arrow


type ForwardedDescriptor = (
    ForwardedObjectMethod[MathematicalObject, ..., object]
    | ForwardedElementMethod[MathematicalElement, ..., object]
    | ForwardedArrowMethod[Arrow, ..., object]
)
