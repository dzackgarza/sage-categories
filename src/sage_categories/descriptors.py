"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from enum import Enum
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


class ParameterRole(Enum):
    """The mathematical role of a parameter or return value."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"
    ITERATOR_ELEMENT = "iterator_element"
    VALUE = "value"


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


def _role_from_type(typ: object) -> ParameterRole:
    if typ is inspect.Parameter.empty or typ is None:
        return ParameterRole.VALUE
    if isinstance(typ, str):
        typ_str = typ.strip()
        if typ_str.startswith(("Iterator[", "collections.abc.Iterator[")):
            inner = typ_str[typ_str.index("[") + 1 : typ_str.rindex("]")].strip()
            if _role_from_type(inner) == ParameterRole.ELEMENT:
                return ParameterRole.ITERATOR_ELEMENT
            return ParameterRole.VALUE
        if typ_str.endswith("Element") or "Element" in typ_str:
            return ParameterRole.ELEMENT
        if typ_str.endswith("Arrow") or typ_str.endswith("Morphism"):
            return ParameterRole.ARROW
        if typ_str.endswith("Object") or typ_str.endswith("Poset") or typ_str.endswith("Set"):
            return ParameterRole.OBJECT
        return ParameterRole.VALUE

    origin = get_origin(typ)
    if origin is not None:
        if isinstance(origin, type) and issubclass(origin, (Iterator,)):
            args = get_args(typ)
            if args and _role_from_type(args[0]) == ParameterRole.ELEMENT:
                return ParameterRole.ITERATOR_ELEMENT
            return ParameterRole.VALUE
        filtered = [a for a in get_args(typ) if a is not type(None)]
        if filtered:
            return _role_from_type(filtered[0])
        return ParameterRole.VALUE

    if isinstance(typ, type):
        if issubclass(typ, Arrow):
            return ParameterRole.ARROW
        if issubclass(typ, MathematicalElement):
            return ParameterRole.ELEMENT
        if issubclass(typ, MathematicalObject):
            return ParameterRole.OBJECT

    return ParameterRole.VALUE


def _inspect_method_roles(
    method: Callable[..., object],
) -> tuple[tuple[tuple[str, ParameterRole], ...], ParameterRole | None, ParameterRole | None, ParameterRole]:
    sig = inspect.signature(method)
    params = list(sig.parameters.values())[1:]
    roles_accumulator: list[tuple[str, ParameterRole]] = []
    var_pos_role: ParameterRole | None = None
    var_kw_role: ParameterRole | None = None
    for p in params:
        role = _role_from_type(p.annotation)
        if p.kind == inspect.Parameter.VAR_POSITIONAL:
            var_pos_role = role
        elif p.kind == inspect.Parameter.VAR_KEYWORD:
            var_kw_role = role
        else:
            roles_accumulator.append((p.name, role))
    return_role = _role_from_type(sig.return_annotation)
    return tuple(roles_accumulator), var_pos_role, var_kw_role, return_role


def _forward_arg_by_role(
    arg: Any,
    role: ParameterRole,
    route: tuple[StructuralFunctor, ...],
) -> Any:
    if arg is None or not route:
        return arg
    source_cat = route[0].domain()
    match role:
        case ParameterRole.OBJECT:
            if arg in source_cat:
                return arg._object_image_along(route)
            return arg
        case ParameterRole.ELEMENT:
            if arg.ambient_object() in source_cat:
                return arg._element_image_along(route)
            return arg
        case ParameterRole.ARROW:
            if arg.domain() in source_cat and arg.codomain() in source_cat:
                return arg._morphism_image_along(route)
            return arg
        case _:
            if isinstance(arg, MathematicalElement) and arg.ambient_object() in source_cat:
                return arg._element_image_along(route)
            if isinstance(arg, MathematicalObject) and arg in source_cat:
                return arg._object_image_along(route)
            if isinstance(arg, Arrow) and arg.domain() in source_cat and arg.codomain() in source_cat:
                return arg._morphism_image_along(route)
            return arg


def _forward_args(
    args: tuple[object, ...],
    param_roles: tuple[tuple[str, ParameterRole], ...],
    var_pos_role: ParameterRole | None,
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
            role = ParameterRole.VALUE
        forwarded.append(_forward_arg_by_role(arg, role, route))
    return tuple(forwarded)


def _forward_kwargs(
    kwargs: dict[str, object],
    param_roles: tuple[tuple[str, ParameterRole], ...],
    var_kw_role: ParameterRole | None,
    route: tuple[StructuralFunctor, ...],
) -> dict[str, object]:
    roles_by_name = dict(param_roles)
    forwarded: dict[str, object] = {}
    for name, val in kwargs.items():
        role = roles_by_name[name] if name in roles_by_name else (var_kw_role if var_kw_role is not None else ParameterRole.VALUE)
        forwarded[name] = _forward_arg_by_role(val, role, route)
    return forwarded


def _transport_result(
    result: Any,
    return_role: ParameterRole,
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

    match return_role:
        case ParameterRole.ITERATOR_ELEMENT:
            assert isinstance(result, Iterator)

            def lazy_elements() -> Iterator[Any]:
                for item in result:
                    yield _pull_back_element_along(item, route, source_ambient)

            return lazy_elements()
        case ParameterRole.ELEMENT:
            return _pull_back_element_along(result, route, source_ambient)
        case _:
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
    ForwardedObjectMethod[MathematicalObject, ..., object] | ForwardedElementMethod[MathematicalElement, ..., object] | ForwardedArrowMethod[Arrow, ..., object]
)
