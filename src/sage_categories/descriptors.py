"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
import types
import typing
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from types import FunctionType
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar, cast

from sage_categories.values import Arrow, MathematicalElement, MathematicalObject

if TYPE_CHECKING:
    from sage_categories.abstract_categories.functors import StructuralFunctor


class ImplementationRole(Enum):
    """The mathematical role of a compiled implementation method."""

    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"


class ParameterRole(Enum):
    """The declared transport role of one method parameter or result."""

    VALUE = "value"
    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"
    ELEMENT_ITERATOR = "element_iterator"
    ELEMENT_COLLECTION = "element_collection"


@dataclass(frozen=True)
class MethodSignature:
    """Role metadata copied from one method declaration."""

    receiver: ParameterRole
    positional: tuple[ParameterRole, ...]
    keyword: tuple[tuple[str, ParameterRole], ...]
    variadic: ParameterRole
    keywords: ParameterRole
    result: ParameterRole

    def role_for_positional(self, position: int) -> ParameterRole:
        if position < len(self.positional):
            return self.positional[position]
        return self.variadic

    def role_for_keyword(self, name: str) -> ParameterRole:
        for declared_name, role in self.keyword:
            if declared_name == name:
                return role
        return self.keywords


@dataclass(frozen=True)
class DeclaredTransportRoles:
    """Explicit role overrides for one mathematical method declaration."""

    positional: tuple[tuple[str, ParameterRole], ...] = ()
    result: ParameterRole | None = None


_DECLARED_TRANSPORT_ROLES: dict[int, DeclaredTransportRoles] = {}


def transport_roles(
    *,
    positional: tuple[tuple[str, ParameterRole], ...] = (),
    result: ParameterRole | None = None,
) -> Callable[[FunctionType], FunctionType]:
    """Attach explicit transport roles to one method declaration."""
    declaration = DeclaredTransportRoles(positional, result)

    def declare(method: FunctionType) -> FunctionType:
        _DECLARED_TRANSPORT_ROLES[id(method)] = declaration
        return method

    return declare


P = ParamSpec("P")
R = TypeVar("R")
Value = TypeVar("Value")
Annotation = TypeVar("Annotation")


def _annotation_role(annotation: Annotation) -> ParameterRole:
    """Read a role from a resolved declaration annotation."""
    if annotation is inspect.Parameter.empty:
        return ParameterRole.VALUE
    if annotation is type(None):
        return ParameterRole.VALUE
    origin = typing.get_origin(annotation)
    if origin is typing.Annotated:
        declared_type, *metadata = typing.get_args(annotation)
        roles = tuple(value for value in metadata if isinstance(value, ParameterRole))
        assert len(roles) == 1, f"{annotation!r} must declare one transport role"
        return roles[0]
    if origin is typing.Union or origin is types.UnionType:
        roles = tuple(
            _annotation_role(argument)
            for argument in typing.get_args(annotation)
            if argument is not type(None)
        )
        assert roles
        return roles[0] if len(set(roles)) == 1 else ParameterRole.VALUE
    if origin is not None:
        if origin is Iterator:
            arguments = typing.get_args(annotation)
            assert len(arguments) == 1
            item_role = _annotation_role(arguments[0])
            if item_role is ParameterRole.ELEMENT:
                return ParameterRole.ELEMENT_ITERATOR
            return ParameterRole.VALUE
        if origin is Iterable:
            arguments = typing.get_args(annotation)
            assert len(arguments) == 1
            item_role = _annotation_role(arguments[0])
            if item_role is ParameterRole.ELEMENT:
                return ParameterRole.ELEMENT_COLLECTION
            return ParameterRole.VALUE
        arguments = typing.get_args(annotation)
        if arguments:
            item_roles = tuple(
                _annotation_role(argument)
                for argument in arguments
                if argument is not Ellipsis
            )
            if all(role is ParameterRole.ELEMENT for role in item_roles):
                return ParameterRole.ELEMENT_COLLECTION
        return ParameterRole.VALUE
    if type(annotation) is type:
        annotation_type = cast(type, annotation)
        if issubclass(annotation_type, Arrow):
            return ParameterRole.ARROW
        if issubclass(annotation_type, MathematicalElement):
            return ParameterRole.ELEMENT
        if issubclass(annotation_type, MathematicalObject):
            return ParameterRole.OBJECT
    return ParameterRole.VALUE


def method_signature(
    method: FunctionType,
    implementation_role: ImplementationRole,
) -> MethodSignature:
    """Return role metadata from the method's declared type annotations."""
    namespace = dict(method.__globals__)
    try:
        annotations = typing.get_type_hints(
            method,
            globalns=namespace,
            localns=namespace,
            include_extras=True,
        )
    except NameError:
        annotations = inspect.get_annotations(method, eval_str=False)
    declared = _DECLARED_TRANSPORT_ROLES.get(id(method))
    declared_positional = dict(declared.positional) if declared is not None else {}
    parameters = tuple(inspect.signature(method).parameters.values())[1:]
    positional: list[ParameterRole] = []
    keyword: list[tuple[str, ParameterRole]] = []
    variadic = ParameterRole.VALUE
    keywords = ParameterRole.VALUE
    for parameter in parameters:
        assert parameter.annotation is not inspect.Parameter.empty, (
            f"{method.__qualname__} must annotate parameter {parameter.name}"
        )
        annotation = annotations[parameter.name] if parameter.name in annotations else parameter.annotation
        role = declared_positional.get(parameter.name, _annotation_role(annotation))
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            variadic = role
        elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
            keywords = role
        elif parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            positional.append(role)
        else:
            keyword.append((parameter.name, role))
    result_annotation = annotations["return"] if "return" in annotations else inspect.signature(method).return_annotation
    assert result_annotation is not inspect.Parameter.empty, (
        f"{method.__qualname__} must annotate its result"
    )
    receiver = {
        ImplementationRole.OBJECT: ParameterRole.OBJECT,
        ImplementationRole.ELEMENT: ParameterRole.ELEMENT,
        ImplementationRole.ARROW: ParameterRole.ARROW,
    }[implementation_role]
    return MethodSignature(
        receiver,
        tuple(positional),
        tuple(keyword),
        variadic,
        keywords,
        declared.result
        if declared is not None and declared.result is not None
        else _annotation_role(result_annotation),
    )


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
    for functor, source in reversed(tuple(zip(route, objects, strict=True))):
        current = functor.preimage_element(source, current)
    return current


def _pull_back_object_along(
    value: MathematicalObject,
    route: tuple[StructuralFunctor, ...],
    source: MathematicalObject,
) -> MathematicalObject:
    current = value
    sources: list[MathematicalObject] = [source]
    prefix: tuple[StructuralFunctor, ...] = ()
    for functor in route[:-1]:
        prefix = (*prefix, functor)
        sources.append(source._object_image_along(prefix))
    for functor, source_object in reversed(tuple(zip(route, sources, strict=True))):
        current = functor.preimage_object(source_object, current)
    return current


def _pull_back_arrow_along(
    value: Arrow,
    route: tuple[StructuralFunctor, ...],
    source: Arrow,
) -> Arrow:
    sources: list[Arrow] = [source]
    prefix: tuple[StructuralFunctor, ...] = ()
    for functor in route[:-1]:
        prefix = (*prefix, functor)
        sources.append(source._morphism_image_along(prefix))
    current = value
    for functor, source_arrow in reversed(tuple(zip(route, sources, strict=True))):
        current = functor.preimage_morphism(source_arrow, current)
    return current


def _forward_value(
    value: Value,
    role: ParameterRole,
    route: tuple[StructuralFunctor, ...],
) -> Value:
    if not route or role is ParameterRole.VALUE:
        return value
    source_category = route[0].domain()
    if role is ParameterRole.OBJECT:
        mathematical_object = cast(MathematicalObject, value)
        value_category = mathematical_object.category()
        if value_category is source_category:
            value_route = route
        else:
            assert value_category.is_subcategory(source_category)
            from sage_categories.compiler import category_compiler

            value_route = category_compiler().implementation_route(
                value_category,
                route[-1].codomain(),
            )
        return cast(Value, mathematical_object._object_image_along(value_route))
    if role is ParameterRole.ELEMENT:
        element = cast(MathematicalElement, value)
        value_category = element.ambient_object().category()
        if not value_category.is_subcategory(source_category):
            return value
        if value_category is source_category:
            value_route = route
        else:
            from sage_categories.compiler import category_compiler

            value_route = category_compiler().implementation_route(
                value_category,
                route[-1].codomain(),
            )
        return cast(Value, element._element_image_along(value_route))
    if role is ParameterRole.ARROW:
        arrow = cast(Arrow, value)
        value_category = arrow.base_category()
        if not value_category.is_subcategory(source_category):
            return value
        if value_category is source_category:
            value_route = route
        else:
            from sage_categories.compiler import category_compiler

            value_route = category_compiler().implementation_route(
                value_category,
                route[-1].codomain(),
            )
        return cast(Value, arrow._morphism_image_along(value_route))
    if role is ParameterRole.ELEMENT_ITERATOR:
        iterator = cast(Iterator[MathematicalElement], value)

        def forward_elements() -> Iterator[MathematicalElement]:
            for element in iterator:
                yield _forward_value(element, ParameterRole.ELEMENT, route)

        return cast(Value, forward_elements())
    assert role is ParameterRole.ELEMENT_COLLECTION
    collection = cast(Iterable[MathematicalElement], value)
    transported = tuple(
        _forward_value(element, ParameterRole.ELEMENT, route)
        for element in collection
    )
    if isinstance(value, tuple):
        return cast(Value, transported)
    if isinstance(value, frozenset):
        return cast(Value, frozenset(transported))
    if isinstance(value, set):
        return cast(Value, set(transported))
    if isinstance(value, list):
        return cast(Value, list(transported))
    return cast(Value, transported)


def _forward_arguments(
    args: tuple[Value, ...],
    kwargs: dict[str, Value],
    signature: MethodSignature,
    route: tuple[StructuralFunctor, ...],
) -> tuple[tuple[Value, ...], dict[str, Value]]:
    forwarded_args = tuple(
        _forward_value(value, signature.role_for_positional(position), route)
        for position, value in enumerate(args)
    )
    forwarded_kwargs = {
        name: _forward_value(value, signature.role_for_keyword(name), route)
        for name, value in kwargs.items()
    }
    return forwarded_args, forwarded_kwargs


def _transport_result(
    result: R,
    role: ParameterRole,
    route: tuple[StructuralFunctor, ...],
    source_ambient: MathematicalObject,
    target_ambient: MathematicalObject,
    instance: MathematicalObject | MathematicalElement | Arrow,
    image: MathematicalObject | MathematicalElement | Arrow,
) -> R:
    if role is ParameterRole.VALUE:
        return result
    if role is ParameterRole.OBJECT:
        value = cast(MathematicalObject, result)
        if value is image or value is target_ambient:
            return cast(R, source_ambient)
        if value not in route[-1].codomain():
            return result
        return cast(R, _pull_back_object_along(value, route, source_ambient))
    if role is ParameterRole.ELEMENT:
        value = cast(MathematicalElement, result)
        if value is image:
            return cast(R, instance)
        if value.ambient_object() not in route[-1].codomain():
            return result
        return cast(R, _pull_back_element_along(value, route, source_ambient))
    if role is ParameterRole.ARROW:
        value = cast(Arrow, result)
        if value is image:
            return cast(R, instance)
        if not value._is_arrow_in(route[-1].codomain()):
            return result
        source_arrow = cast(Arrow, instance)
        return cast(R, _pull_back_arrow_along(value, route, source_arrow))
    if role is ParameterRole.ELEMENT_ITERATOR:
        iterator = cast(Iterator[MathematicalElement], result)

        def pull_back_elements() -> Iterator[MathematicalElement]:
            for element in iterator:
                yield _pull_back_element_along(element, route, source_ambient)

        return cast(R, pull_back_elements())
    assert role is ParameterRole.ELEMENT_COLLECTION
    collection = cast(Iterable[MathematicalElement], result)
    transported = tuple(
        _pull_back_element_along(element, route, source_ambient)
        for element in collection
    )
    if isinstance(result, tuple):
        return cast(R, transported)
    if isinstance(result, frozenset):
        return cast(R, frozenset(transported))
    if isinstance(result, set):
        return cast(R, set(transported))
    if isinstance(result, list):
        return cast(R, list(transported))
    return cast(R, transported)


class ForwardedObjectMethod[Receiver: MathematicalObject, **P, R]:
    """Forward an object method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[MathematicalObject, P], R],
        signature: MethodSignature,
    ) -> None:
        assert route
        self._route = route
        self._method: FunctionType = cast(FunctionType, method)
        assert signature.receiver is ParameterRole.OBJECT
        self._signature = signature

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedObjectMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self
        image = instance._object_image_along(self._route)
        route = self._route
        method = self._method
        signature = self._signature

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args, forwarded_kwargs = _forward_arguments(
                tuple(args),
                dict(kwargs),
                signature,
                route,
            )
            result = cast(R, method(image, *forwarded_args, **forwarded_kwargs))
            return _transport_result(result, signature.result, route, instance, image, instance, image)

        return call


class ForwardedElementMethod[Receiver: MathematicalElement, **P, R]:
    """Forward an element method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[MathematicalElement, P], R],
        signature: MethodSignature,
    ) -> None:
        assert route
        self._route = route
        self._method: FunctionType = cast(FunctionType, method)
        assert signature.receiver is ParameterRole.ELEMENT
        self._signature = signature

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedElementMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self
        image = instance._element_image_along(self._route)
        source_ambient = instance.ambient_object()
        route = self._route
        method = self._method
        signature = self._signature

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args, forwarded_kwargs = _forward_arguments(
                tuple(args),
                dict(kwargs),
                signature,
                route,
            )
            result = cast(R, method(image, *forwarded_args, **forwarded_kwargs))
            return _transport_result(result, signature.result, route, source_ambient, image.ambient_object(), instance, image)

        return call


class ForwardedArrowMethod[Receiver: Arrow, **P, R]:
    """Forward an arrow method along a structural-functor route."""

    def __init__(
        self,
        route: tuple[StructuralFunctor, ...],
        method: Callable[Concatenate[Arrow, P], R],
        signature: MethodSignature,
    ) -> None:
        assert route
        self._route = route
        self._method: FunctionType = cast(FunctionType, method)
        assert signature.receiver is ParameterRole.ARROW
        self._signature = signature

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedArrowMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self
        image = instance._morphism_image_along(self._route)
        route = self._route
        method = self._method
        signature = self._signature

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args, forwarded_kwargs = _forward_arguments(
                tuple(args),
                dict(kwargs),
                signature,
                route,
            )
            result = cast(R, method(image, *forwarded_args, **forwarded_kwargs))
            return _transport_result(result, signature.result, route, instance.codomain(), image.codomain(), instance, image)

        return call


type ForwardedDescriptor = ForwardedObjectMethod | ForwardedElementMethod | ForwardedArrowMethod
