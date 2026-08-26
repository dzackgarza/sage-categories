"""Role extraction from typed signatures (D13, POL-KERNEL-021/024).

A declaring method's ordinary Python signature is its sole authoritative
declaration (POL-CAT-075).  The receiver role comes from the declaring role class;
parameter and result roles from exact annotations, read against the declaring
category's own role classes:

- the declaring category's role class, one of its bases below the kernel base, or
  a refinement of it (``SetObject`` on ``Sets()``, ``Category`` or ``Functor`` on
  ``Cat()``) is that transportable role: the argument is a value of the declaring
  category's lineage and is transported along the receiver's route;
- a bare kernel base (``ObjectOfCategory``, ``ElementOfObject``,
  ``MorphismOfCategory``, ``CategoryPoint``) is a point of the receiver's own
  category, or of a category the receiver determines (an object of a category
  ``C`` in a method of ``Cat().ObjectType``; an object of the index category in a
  product's ``product_projection``).  The receiver's route acts on the receiver,
  not on such a point: the point is admitted exactly when the receiver's image is
  the receiver itself, and rejected otherwise;
- ``Self`` is the receiver's role;
- a union of one transportable role with plain value types (``CardinalObject | int``)
  is that role admitting a plain datum: an owned argument is transported and a
  plain datum passes unchanged;
- the role class of another category (``DiscreteObject`` in a method of a
  ``Sets()`` family), ``Cardinal | UnknownClass``, ``Decision``, ``AppliedPredicate``,
  ``bool``, ``int``, ``str``, ``None``, an exact ``Callable[[...], ...]`` and other
  exact non-role types are plain values: passed unchanged, since the receiver's
  route has no action on them;
- ``Iterator[role]`` is a lazy family of that role, transported item by item;
- ``Any`` is admitted only as the ``candidate`` of ``__eq__``, ``__ne__``,
  ``__contains__``, and ``membership_proposition`` (POL-TYPE-004).

Unknown or broad roles (``Any`` elsewhere, ``object``, ``Callable[..., Any]``, a
union mixing two transportable roles, a missing annotation) fail descriptor
construction with the declaration named.
"""

from __future__ import annotations

import inspect
import types
import typing
from collections.abc import Callable, Iterator
from enum import Enum
from typing import TYPE_CHECKING, Any, NamedTuple

from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["ArgumentRole", "ParameterRole", "Signature", "declared_signature"]


class ArgumentRole(Enum):
    OBJECT = "object"
    ELEMENT = "element"
    MORPHISM = "morphism"
    OBJECT_FAMILY = "iterator of objects"
    ELEMENT_FAMILY = "iterator of elements"
    MORPHISM_FAMILY = "iterator of morphisms"
    RECEIVER_POINT = "point of the receiver's category"
    VALUE = "value"
    CANDIDATE = "candidate"


class ParameterRole(NamedTuple):
    role: ArgumentRole
    admits_value: bool


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

_ITEM: dict[ArgumentRole, Role] = {family: _TRANSPORTED[role] for role, family in _FAMILY.items()}

_OF_ROLE: dict[Role, ArgumentRole] = {
    Role.OBJECT: ArgumentRole.OBJECT,
    Role.ELEMENT: ArgumentRole.ELEMENT,
    Role.MORPHISM: ArgumentRole.MORPHISM,
}

_KERNEL_BASES = (ObjectOfCategory, ElementOfObject, MorphismOfCategory, CategoryPoint)

_CANDIDATE_METHODS = ("__eq__", "__ne__", "__contains__", "membership_proposition")


class Signature:
    def __init__(self, parameters: dict[str, ParameterRole], result: ArgumentRole) -> None:
        self._parameters = parameters
        self._result = result

    def parameters(self) -> dict[str, ParameterRole]:
        return self._parameters

    def result(self) -> ArgumentRole:
        return self._result

    @staticmethod
    def transported_role(argument_role: ArgumentRole) -> Role | None:
        """The kernel role a transported argument must have, for a value role or a family role."""
        return _TRANSPORTED.get(argument_role, _ITEM.get(argument_role))

    @staticmethod
    def is_family(argument_role: ArgumentRole) -> bool:
        return argument_role in _ITEM


class _Context:
    """The declaring category's compiled role classes and the receiver's role."""

    def __init__(self, owner: Category, receiver: Role) -> None:
        self.roles = {role: owner.role_class(role) for role in Role}
        self.receiver = receiver

    def role_of_class(self, annotation: type) -> ArgumentRole:
        if annotation in _KERNEL_BASES:
            return ArgumentRole.RECEIVER_POINT
        if not issubclass(annotation, CategoryPoint):
            return ArgumentRole.VALUE
        for role, role_class in self.roles.items():
            if issubclass(role_class, annotation) or issubclass(annotation, role_class):
                return _OF_ROLE[role]
        return ArgumentRole.VALUE


def _classify(annotation: Any, declaration: str, context: _Context) -> ParameterRole:
    if annotation is inspect.Parameter.empty:
        raise TypeError(f"{declaration}: every parameter and the result need an exact annotation")
    if annotation is Any or annotation is object:
        raise TypeError(f"{declaration}: {annotation!r} is not an exact role")
    if annotation is None or annotation is type(None) or annotation is Ellipsis:
        return ParameterRole(ArgumentRole.VALUE, True)
    if isinstance(annotation, (typing.TypeVar, typing.ParamSpec, typing.ParamSpecArgs, typing.ParamSpecKwargs, list, tuple)):
        # A type parameter of the declaring class, or a parameter-list substitution
        # for one, is generic construction data rather than a mathematical role.
        return ParameterRole(ArgumentRole.VALUE, True)
    if isinstance(annotation, typing.TypeAliasType):
        return _classify(annotation.__value__, declaration, context)
    if annotation is typing.Self:
        return ParameterRole(_OF_ROLE[context.receiver], False)
    origin = typing.get_origin(annotation)
    if origin is types.UnionType or origin is typing.Union:
        members = [_classify(member, declaration, context) for member in typing.get_args(annotation)]
        roles = [member.role for member in members if member.role is not ArgumentRole.VALUE]
        if len(roles) > 1:
            raise TypeError(f"{declaration}: a union of several mathematical roles is type erasure")
        admits_value = any(member.role is ArgumentRole.VALUE for member in members)
        return ParameterRole(roles[0] if roles else ArgumentRole.VALUE, admits_value)
    if origin is Iterator or origin is typing.Iterator:
        (item,) = typing.get_args(annotation)
        return ParameterRole(_FAMILY.get(_classify(item, declaration, context).role, ArgumentRole.VALUE), False)
    if origin is Callable or origin is typing.Callable:
        arguments, result = typing.get_args(annotation)
        if arguments is Ellipsis or result is Any or result is object:
            raise TypeError(f"{declaration}: {annotation!r} is not an exact callable type")
        for argument in arguments:
            _classify(argument, declaration, context)
        _classify(result, declaration, context)
        return ParameterRole(ArgumentRole.VALUE, True)
    if origin is not None:
        for argument in typing.get_args(annotation):
            _classify(argument, declaration, context)
        return ParameterRole(ArgumentRole.VALUE, True)
    if isinstance(annotation, type):
        role = context.role_of_class(annotation)
        return ParameterRole(role, role is ArgumentRole.VALUE)
    raise TypeError(f"{declaration}: {annotation!r} is not an exact role")


def declared_signature(function: Callable[..., Any], declaration: str, owner: Category, receiver: Role) -> Signature:
    """Extract the exact argument and result roles of a declaring method of ``owner``.

    Annotations are evaluated with the type parameters of the declaring role class
    in scope, since a generic class's methods name them (``Category[MorphismData,
    TwoMorphismData]``).
    """
    declaring_class = owner.local_role_class(receiver)
    type_parameters = {
        parameter.__name__: parameter for klass in reversed(declaring_class.__mro__) for parameter in getattr(klass, "__type_params__", ())
    }
    context = _Context(owner, receiver)
    signature = inspect.signature(function, eval_str=True, locals=type_parameters)
    parameters: dict[str, ParameterRole] = {}
    for index, (name, parameter) in enumerate(signature.parameters.items()):
        if index == 0:
            continue
        if name == "candidate" and function.__name__ in _CANDIDATE_METHODS:
            parameters[name] = ParameterRole(ArgumentRole.CANDIDATE, True)
            continue
        parameters[name] = _classify(parameter.annotation, declaration, context)
    result_annotation = signature.return_annotation
    if result_annotation is inspect.Signature.empty:
        raise TypeError(f"{declaration}: the result needs an exact annotation")
    return Signature(parameters, _classify(result_annotation, declaration, context).role)
