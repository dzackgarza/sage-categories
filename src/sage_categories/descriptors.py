"""Descriptors for functorial method inheritance."""

from __future__ import annotations

import inspect
import types
import typing
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from types import FunctionType
from typing import TYPE_CHECKING, Concatenate, ParamSpec, TypeVar, assert_never, cast

from sage_categories.values import (
    Arrow,
    Decision,
    ImplementationRole,
    MathematicalElement,
    MathematicalObject,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.full_subcategories import FullSubcategory
    from sage_categories.abstract_categories.functors import Functor
    from sage_categories.category import Category


class ParameterRole(Enum):
    """A compiler-owned transport role or explicit absence marker."""

    ABSENT = "absent"
    VALUE = "value"
    OBJECT = "object"
    ELEMENT = "element"
    ARROW = "arrow"
    OBJECT_ITERATOR = "object_iterator"
    ELEMENT_ITERATOR = "element_iterator"
    ARROW_ITERATOR = "arrow_iterator"


_PARAMETER_ROLE_FOR_IMPLEMENTATION = {
    ImplementationRole.OBJECT: ParameterRole.OBJECT,
    ImplementationRole.ELEMENT: ParameterRole.ELEMENT,
    ImplementationRole.ARROW: ParameterRole.ARROW,
}

_IMPLEMENTATION_ROLE_FOR_PARAMETER = {
    parameter_role: implementation_role
    for implementation_role, parameter_role in _PARAMETER_ROLE_FOR_IMPLEMENTATION.items()
}


@dataclass(frozen=True)
class MethodSignature:
    """Role metadata derived from one exact method declaration."""

    receiver: ParameterRole
    positional: tuple[ParameterRole, ...]
    keyword: tuple[tuple[str, ParameterRole], ...]
    variadic: ParameterRole
    keywords: ParameterRole
    result: ParameterRole

    def role_for_positional(self, position: int) -> ParameterRole:
        if position < len(self.positional):
            return self.positional[position]
        assert self.variadic is not ParameterRole.ABSENT
        return self.variadic

    def role_for_keyword(self, name: str) -> ParameterRole:
        for declared_name, role in self.keyword:
            if declared_name == name:
                return role
        assert self.keywords is not ParameterRole.ABSENT
        return self.keywords


P = ParamSpec("P")
R = TypeVar("R")
Value = TypeVar("Value")


def _annotation_role(
    annotation: object,
    receiver: ParameterRole,
    method_name: str,
) -> ParameterRole:
    """Resolve one exact mathematical type inside the compiler."""
    if isinstance(annotation, typing.TypeAliasType):
        return _annotation_role(annotation.__value__, receiver, method_name)
    if annotation is typing.Self:
        return receiver
    if annotation is None or annotation is types.NoneType:
        return ParameterRole.VALUE
    if annotation is typing.Any:
        assert method_name in ("__contains__", "__eq__")
        return ParameterRole.VALUE
    if isinstance(annotation, type):
        if issubclass(annotation, Arrow):
            return ParameterRole.ARROW
        if issubclass(annotation, MathematicalElement):
            return ParameterRole.ELEMENT
        if issubclass(annotation, MathematicalObject):
            return ParameterRole.OBJECT
        if issubclass(annotation, Enum):
            return ParameterRole.VALUE
        assert annotation in (bool, int, float, str, bytes) or (
            annotation is object and method_name == "__eq__"
        ), f"{annotation!r} has no exact mathematical transport role"
        return ParameterRole.VALUE
    origin = typing.get_origin(annotation)
    assert origin is not typing.Annotated
    if origin in (typing.Union, types.UnionType):
        arguments = typing.get_args(annotation)
        assert types.NoneType not in arguments, (
            f"{annotation!r} is not a total mathematical signature"
        )
        roles = {
            _annotation_role(argument, receiver, method_name)
            for argument in arguments
        }
        assert len(roles) == 1, f"{annotation!r} combines transport roles"
        return roles.pop()
    if origin is Iterator:
        assert method_name == "__iter__", (
            f"{annotation!r} is traversal output, not a mathematical collection"
        )
        arguments = typing.get_args(annotation)
        assert len(arguments) == 1
        item_role = _annotation_role(arguments[0], receiver, method_name)
        return {
            ParameterRole.OBJECT: ParameterRole.OBJECT_ITERATOR,
            ParameterRole.ELEMENT: ParameterRole.ELEMENT_ITERATOR,
            ParameterRole.ARROW: ParameterRole.ARROW_ITERATOR,
        }[item_role]
    if origin in (Callable, typing.Literal, typing.TypeIs):
        return ParameterRole.VALUE
    assert False, f"{annotation!r} has no exact mathematical transport role"


def method_signature(
    method: FunctionType,
    implementation_role: ImplementationRole,
) -> MethodSignature:
    """Return the method's complete transport roles from its exact types."""
    signature = inspect.signature(method)
    annotations = typing.get_type_hints(method, include_extras=True)
    assert "return" in annotations, (
        f"{method.__qualname__} has no mathematical result type"
    )
    parameters = tuple(signature.parameters.values())
    assert parameters
    receiver = _PARAMETER_ROLE_FOR_IMPLEMENTATION[implementation_role]
    positional: list[ParameterRole] = []
    keyword: list[tuple[str, ParameterRole]] = []
    variadic = ParameterRole.ABSENT
    keywords = ParameterRole.ABSENT
    for parameter in parameters[1:]:
        assert parameter.name in annotations, (
            f"{method.__qualname__} parameter {parameter.name} has no mathematical type"
        )
        role = _annotation_role(
            annotations[parameter.name],
            receiver,
            method.__name__,
        )
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
    return MethodSignature(
        receiver,
        tuple(positional),
        tuple(keyword),
        variadic,
        keywords,
        _annotation_role(
            annotations["return"],
            receiver,
            method.__name__,
        ),
    )


def _pull_back_element_along(
    element: MathematicalElement,
    route: tuple[Functor, ...],
    source_ambient: MathematicalObject,
) -> MathematicalElement:
    objects: list[MathematicalObject] = [source_ambient]
    prefix: tuple[Functor, ...] = ()
    for functor in route[:-1]:
        prefix = (*prefix, functor)
        objects.append(source_ambient._object_image_along(prefix))
    current = element
    for functor, source in reversed(tuple(zip(route, objects, strict=True))):
        current = functor.preimage_element(source, current)
    return current


_ITERATOR_ITEM_ROLES = {
    ParameterRole.OBJECT_ITERATOR: ParameterRole.OBJECT,
    ParameterRole.ELEMENT_ITERATOR: ParameterRole.ELEMENT,
    ParameterRole.ARROW_ITERATOR: ParameterRole.ARROW,
}


def _implementation_route(
    source: Category,
    target: Category,
) -> tuple[Functor, ...]:
    from sage_categories.compiler import category_compiler

    return category_compiler().implementation_route(source, target)


def _forward_value(
    value: Value,
    role: ParameterRole,
    route: tuple[Functor, ...],
) -> Value:
    assert role is not ParameterRole.ABSENT
    if not route or role is ParameterRole.VALUE:
        return value
    source_category = route[0].domain()
    if role is ParameterRole.OBJECT:
        mathematical_object = cast(MathematicalObject, value)
        value_category = mathematical_object.category()
        if not value_category.is_subcategory(source_category):
            return value
        value_route = (
            route
            if value_category is source_category
            else _implementation_route(value_category, route[-1].codomain())
        )
        return cast(Value, mathematical_object._object_image_along(value_route))
    if role is ParameterRole.ELEMENT:
        element = cast(MathematicalElement, value)
        value_category = element.ambient_object().category()
        if not value_category.is_subcategory(source_category):
            return value
        value_route = (
            route
            if value_category is source_category
            else _implementation_route(value_category, route[-1].codomain())
        )
        return cast(Value, element._element_image_along(value_route))
    if role is ParameterRole.ARROW:
        arrow = cast(Arrow, value)
        value_category = arrow.base_category()
        if not value_category.is_subcategory(source_category):
            return value
        value_route = (
            route
            if value_category is source_category
            else _implementation_route(value_category, route[-1].codomain())
        )
        return cast(Value, arrow._morphism_image_along(value_route))
    item_role = _ITERATOR_ITEM_ROLES.get(role)
    if item_role is not None:
        iterator = cast(Iterator[MathematicalObject], value)

        def forward_values() -> Iterator[MathematicalObject]:
            for item in iterator:
                yield _forward_value(item, item_role, route)

        return cast(Value, forward_values())
    assert_never(role)


def _forward_arguments(
    args: tuple[Value, ...],
    kwargs: dict[str, Value],
    signature: MethodSignature,
    route: tuple[Functor, ...],
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
    route: tuple[Functor, ...],
    source_ambient: MathematicalObject,
    target_ambient: MathematicalObject,
    instance: MathematicalObject,
    image: MathematicalObject,
) -> R:
    assert role is not ParameterRole.ABSENT
    if role is ParameterRole.VALUE:
        return result
    if role is ParameterRole.OBJECT:
        value = cast(MathematicalObject, result)
        if value is target_ambient:
            return cast(R, source_ambient)
        return result
    if role is ParameterRole.ELEMENT:
        value = cast(MathematicalElement, result)
        if value is image:
            return cast(R, instance)
        if value.ambient_object() is not target_ambient:
            return result
        return cast(R, _pull_back_element_along(value, route, source_ambient))
    if role is ParameterRole.ARROW:
        value = cast(Arrow, result)
        if value is image:
            return cast(R, instance)
        return result
    item_role = _ITERATOR_ITEM_ROLES.get(role)
    if item_role is not None:
        iterator = cast(Iterator[MathematicalObject], result)

        def pull_back_values() -> Iterator[MathematicalObject]:
            for value in iterator:
                yield _transport_result(
                    value,
                    item_role,
                    route,
                    source_ambient,
                    target_ambient,
                    instance,
                    image,
                )

        return cast(R, pull_back_values())
    assert_never(role)


type ForwardedDeclaration = tuple[
    tuple[Functor, ...],
    FunctionType,
    MethodSignature,
]


class ForwardedMethod[Receiver: MathematicalObject, **P, R]:
    """Forward one spelling across every category-owned implementation role."""

    def __init__(
        self,
        category: Category,
        route: tuple[Functor, ...],
        method: Callable[Concatenate[MathematicalObject, P], R],
        signature: MethodSignature,
    ) -> None:
        self._declarations: dict[
            tuple[int, ImplementationRole],
            ForwardedDeclaration,
        ] = {}
        self.register(category, route, method, signature)

    def register(
        self,
        category: Category,
        route: tuple[Functor, ...],
        method: Callable[Concatenate[MathematicalObject, P], R],
        signature: MethodSignature,
    ) -> None:
        assert route, method.__qualname__
        implementation_role = _IMPLEMENTATION_ROLE_FOR_PARAMETER.get(
            signature.receiver
        )
        assert implementation_role is not None
        declaration = route, cast(FunctionType, method), signature
        key = id(category), implementation_role
        previous = self._declarations.get(key)
        assert previous is None or previous == declaration
        self._declarations[key] = declaration

    def _applicable(
        self,
        instance: MathematicalObject,
    ) -> tuple[ForwardedDeclaration, ...]:
        candidates: list[ForwardedDeclaration] = []
        for implementation_role, category in instance._implementation_contexts():
            declaration = self._declarations.get(
                (id(category), implementation_role)
            )
            if declaration is not None:
                candidates.append(declaration)
        return tuple(candidates)

    def _declaration(
        self,
        instance: MathematicalObject,
    ) -> ForwardedDeclaration:
        applicable = self._applicable(instance)
        assert applicable, (
            f"{type(instance).__qualname__} has no forwarding declaration "
            f"for {instance.category()}"
        )
        selected = applicable[0]
        selected_method = selected[1]
        assert all(declaration[1] is selected_method for declaration in applicable), (
            f"{type(instance).__qualname__} inherits this spelling with different "
            "mathematical meanings in overlapping implementation roles"
        )
        return selected

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> ForwardedMethod[Receiver, P, R] | Callable[P, R]:
        if instance is None:
            return self
        route, method, signature = self._declaration(instance)
        implementation_role = _IMPLEMENTATION_ROLE_FOR_PARAMETER.get(
            signature.receiver
        )
        assert implementation_role is not None
        image = instance._implementation_image(implementation_role, route)
        source_ambient = instance._implementation_ambient(implementation_role)
        target_ambient = image._implementation_ambient(implementation_role)

        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            forwarded_args, forwarded_kwargs = _forward_arguments(
                tuple(args),
                dict(kwargs),
                signature,
                route,
            )
            result = cast(R, method(image, *forwarded_args, **forwarded_kwargs))
            return _transport_result(
                result,
                signature.result,
                route,
                source_ambient,
                target_ambient,
                instance,
                image,
            )

        return call


ForwardedObjectMethod = ForwardedMethod
ForwardedElementMethod = ForwardedMethod
ForwardedArrowMethod = ForwardedMethod
type ForwardedDescriptor = ForwardedMethod


class RefiningPropertyMethod[Receiver: MathematicalObject]:
    """Refine a value after its ambient predicate returns exact ``True``."""

    def __init__(
        self,
        ambient_category: Category,
        property_category: FullSubcategory,
        method: Callable[[Receiver], Decision],
    ) -> None:
        self._declarations: dict[
            int,
            tuple[FullSubcategory, Callable[[Receiver], Decision]],
        ] = {}
        self.register(ambient_category, property_category, method)

    def register(
        self,
        ambient_category: Category,
        property_category: FullSubcategory,
        method: Callable[[Receiver], Decision],
    ) -> None:
        declaration = property_category, method
        previous = self._declarations.get(id(ambient_category))
        assert previous is None or previous == declaration
        self._declarations[id(ambient_category)] = declaration

    def declaration(self) -> FunctionType:
        methods = tuple(
            declaration[1]
            for declaration in self._declarations.values()
        )
        assert methods
        assert all(method is methods[0] for method in methods)
        return cast(FunctionType, methods[0])

    def __get__(
        self,
        instance: Receiver | None,
        owner: type[Receiver] | None = None,
    ) -> RefiningPropertyMethod[Receiver] | Callable[[], Decision]:
        if instance is None:
            return self
        property_category, method = self._declarations[id(instance.category())]

        def call() -> Decision:
            from sage_categories.assumptions import assumption_decision

            assumed = assumption_decision(property_category.predicate(instance))
            if assumed is True:
                property_category(instance)
                return True
            if assumed is False:
                return False
            decision = method(instance)
            if decision is True:
                property_category(instance)
            return decision

        return call
