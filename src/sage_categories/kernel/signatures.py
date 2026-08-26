"""Role extraction from typed signatures (D13, POL-KERNEL-021/024).

A declaring method's ordinary Python signature is its sole authoritative
declaration (POL-CAT-075).  The receiver role comes from the declaring role class;
parameter and result roles from exact annotations:

- a subclass of ``ObjectOfCategory`` / ``ElementOfObject`` / ``MorphismOfCategory``
  is that transportable role; ``CategoryPoint`` itself is the exact union of the
  three (a value transported by its own role), used by functor application;
- a union of one transportable role with plain value types (``CardinalObject | int``)
  is that role: an owned argument is transported and a plain datum passes unchanged;
- ``Cardinal | UnknownClass``, ``Decision``, ``AppliedPredicate``, ``bool``, ``int``,
  ``str``, ``None``, a category, an exact ``Callable[[...], ...]`` and other exact
  non-role types are plain values: returned or passed unchanged;
- ``Iterator[role]`` is a lazy family of that role (``__iter__``);
- ``Any`` is admitted only as the ``candidate`` of ``__eq__``, ``__ne__``, and
  ``__contains__`` (POL-TYPE-004).

Unknown or broad roles (``Any`` elsewhere, ``object``, ``Callable[..., Any]``, a
union mixing a transportable role with anything else, a missing annotation) fail
descriptor construction with the declaration named.
"""

from __future__ import annotations

import inspect
import types
import typing
from collections.abc import Callable, Iterator
from enum import Enum
from typing import Any

from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

__all__ = ["ArgumentRole", "Signature", "declared_signature"]


class ArgumentRole(Enum):
    OBJECT = "object"
    ELEMENT = "element"
    MORPHISM = "morphism"
    POINT = "object, element, or morphism"
    OBJECT_FAMILY = "iterator of objects"
    ELEMENT_FAMILY = "iterator of elements"
    MORPHISM_FAMILY = "iterator of morphisms"
    VALUE = "value"
    CANDIDATE = "candidate"


_TRANSPORTED: dict[ArgumentRole, Role] = {
    ArgumentRole.OBJECT: Role.OBJECT,
    ArgumentRole.ELEMENT: Role.ELEMENT,
    ArgumentRole.MORPHISM: Role.MORPHISM,
}

_FAMILY: dict[ArgumentRole, ArgumentRole] = {
    ArgumentRole.OBJECT: ArgumentRole.OBJECT_FAMILY,
    ArgumentRole.ELEMENT: ArgumentRole.ELEMENT_FAMILY,
    ArgumentRole.MORPHISM: ArgumentRole.MORPHISM_FAMILY,
}

_CANDIDATE_METHODS = ("__eq__", "__ne__", "__contains__")


class Signature:
    def __init__(self, parameters: dict[str, ArgumentRole], result: ArgumentRole) -> None:
        self._parameters = parameters
        self._result = result

    def parameters(self) -> dict[str, ArgumentRole]:
        return self._parameters

    def result(self) -> ArgumentRole:
        return self._result

    @staticmethod
    def transported_role(argument_role: ArgumentRole) -> Role | None:
        return _TRANSPORTED.get(argument_role)


def _role_of_class(annotation: type) -> ArgumentRole:
    if issubclass(annotation, ObjectOfCategory):
        return ArgumentRole.OBJECT
    if issubclass(annotation, ElementOfObject):
        return ArgumentRole.ELEMENT
    if issubclass(annotation, MorphismOfCategory):
        return ArgumentRole.MORPHISM
    if issubclass(annotation, CategoryPoint):
        return ArgumentRole.POINT
    return ArgumentRole.VALUE


def _classify(annotation: Any, declaration: str) -> ArgumentRole:
    if annotation is inspect.Parameter.empty:
        raise TypeError(f"{declaration}: every parameter and the result need an exact annotation")
    if annotation is Any or annotation is object:
        raise TypeError(f"{declaration}: {annotation!r} is not an exact role")
    if annotation is None or annotation is type(None) or annotation is Ellipsis:
        return ArgumentRole.VALUE
    if isinstance(annotation, (typing.TypeVar, typing.ParamSpec, typing.ParamSpecArgs, typing.ParamSpecKwargs, list, tuple)):
        # A type parameter of the declaring class, or a parameter-list substitution
        # for one, is generic construction data rather than a mathematical role.
        return ArgumentRole.VALUE
    if isinstance(annotation, typing.TypeAliasType):
        return _classify(annotation.__value__, declaration)
    origin = typing.get_origin(annotation)
    if origin is types.UnionType or origin is typing.Union:
        members = [_classify(member, declaration) for member in typing.get_args(annotation)]
        roles = [member for member in members if member is not ArgumentRole.VALUE]
        if len(roles) > 1:
            raise TypeError(f"{declaration}: a union of several mathematical roles is type erasure")
        return roles[0] if roles else ArgumentRole.VALUE
    if origin is Iterator or origin is typing.Iterator:
        (item,) = typing.get_args(annotation)
        return _FAMILY.get(_classify(item, declaration), ArgumentRole.VALUE)
    if origin is Callable or origin is typing.Callable:
        arguments, result = typing.get_args(annotation)
        if arguments is Ellipsis or result is Any or result is object:
            raise TypeError(f"{declaration}: {annotation!r} is not an exact callable type")
        for argument in arguments:
            _classify(argument, declaration)
        _classify(result, declaration)
        return ArgumentRole.VALUE
    if origin is not None:
        for argument in typing.get_args(annotation):
            _classify(argument, declaration)
        return ArgumentRole.VALUE
    if isinstance(annotation, type):
        return _role_of_class(annotation)
    if annotation is typing.Self:
        return ArgumentRole.VALUE
    raise TypeError(f"{declaration}: {annotation!r} is not an exact role")


def declared_signature(function: Callable[..., Any], declaration: str, declaring_class: type) -> Signature:
    """Extract the exact argument and result roles of a declaring method.

    Annotations are evaluated with the type parameters of the declaring role class
    in scope, since a generic class's methods name them (``Category[MorphismData,
    TwoMorphismData]``).
    """
    type_parameters = {
        parameter.__name__: parameter for klass in reversed(declaring_class.__mro__) for parameter in getattr(klass, "__type_params__", ())
    }
    signature = inspect.signature(function, eval_str=True, locals=type_parameters)
    parameters: dict[str, ArgumentRole] = {}
    for index, (name, parameter) in enumerate(signature.parameters.items()):
        if index == 0:
            continue
        if name == "candidate" and function.__name__ in _CANDIDATE_METHODS:
            parameters[name] = ArgumentRole.CANDIDATE
            continue
        parameters[name] = _classify(parameter.annotation, declaration)
    result_annotation = signature.return_annotation
    if result_annotation is inspect.Signature.empty:
        raise TypeError(f"{declaration}: the result needs an exact annotation")
    return Signature(parameters, _classify(result_annotation, declaration))
