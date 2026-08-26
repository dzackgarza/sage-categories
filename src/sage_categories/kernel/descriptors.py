"""Forwarding descriptors and structural transport (D11, D13, D18).

An inherited method means composition: ``X.f(...) := F(X).f(...)``.  The descriptor
transports the receiver and every transportable argument forward to the declaring
node, calls the declaring method on the images, and returns its value unchanged
(there is no result branch, D18).

Transport is canonical: one image per value and reachable category, stored in
the identity-keyed tables of ``kernel/caches.py``.  At the first transport of a
value to a node, every selected route to that node is traversed in declaration
order; the first image is stored and each later image must be the same object
(POL-CAT-012).  A mismatch raises ``StructuralImageMismatch`` naming the source
construction, both routes, and the shared category; nothing is repaired.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.caches import canonical_images
from sage_categories.kernel.roles import CategoryPoint, Role, role_of
from sage_categories.kernel.signatures import ArgumentRole, Signature, declared_signature

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "ForwardedElementMethod",
    "ForwardedMethod",
    "ForwardedMorphismMethod",
    "ForwardedObjectMethod",
    "forwarding_descriptor",
    "placement_node",
    "transport",
]


def placement_node(value: CategoryPoint) -> compiler.Node:
    """The node in which ``value`` currently lives: objects and morphisms as objects of their placement."""
    match role_of(value):
        case Role.OBJECT | Role.MORPHISM:
            return compiler.node(value.category(), Role.OBJECT)
        case Role.ELEMENT:
            return compiler.node(value.parent().category(), Role.ELEMENT)
    raise AssertionError(f"{value!r} is not an owned value")


def _apply(functor: Functor, step_role: Role, value: CategoryPoint) -> CategoryPoint:
    # The action is the one ``Cat()`` declares on its morphism role, invoked directly:
    # a functor placed in a property subcategory of ``Fun`` reaches the same declaration
    # through an identity-on-value inclusion, so the value is the same (D08).
    declared = functor.base_category().local_role_class(Role.MORPHISM)
    match step_role:
        case Role.OBJECT:
            return declared.on_object(functor, value)
        case Role.MORPHISM:
            return declared.on_morphism(functor, value)
        case Role.ELEMENT:
            return _apply_to_element(functor, declared, value)
    raise AssertionError(step_role)


def _is_classical(element: CategoryPoint, category: Category) -> bool:
    return any(element.stage() is stage for stage in category.classical_stages())


def _apply_to_element(functor: Functor, declared: type, element: CategoryPoint) -> CategoryPoint:
    # A classical element ``t: G_C -> X`` reaches the classical stage of the codomain
    # through the stage comparison ``c: G_D -> F(G_C)`` retained by the selected functor:
    # its image is the element ``F(t) after c`` (``specs/functor.md``, "Structural
    # inheritance"; POL-CAT-062).  The identity comparison, retained when ``F(G_C) is
    # G_D``, changes nothing.
    if not _is_classical(element, functor.domain()) or not functor.codomain().classical_stages():
        return declared.on_element(functor, element)
    comparison = functor.stage_comparison()
    if comparison is comparison.domain().identity():
        return declared.on_element(functor, element)
    image = declared.on_morphism(functor, element.defining_morphism()) * comparison
    return functor.codomain().element_from_defining_morphism(image)


def _apply_route(value: CategoryPoint, route: compiler.Route) -> CategoryPoint:
    image = value
    for functor, step_role in route:
        image = _apply(functor, step_role, image)
    return image


def _route_name(route: compiler.Route) -> str:
    return " then ".join(repr(functor) for functor, _ in route) or "the identity route"


def transport(value: CategoryPoint, target: compiler.Node) -> CategoryPoint:
    """The canonical image of ``value`` at ``target``, established at first transport."""
    source = placement_node(value)
    if compiler.same_node(source, target):
        return value
    role = role_of(value)
    assert role is not None
    table = canonical_images[role]
    first_key = value.parent() if role is Role.ELEMENT else value
    key = (first_key, value, target.category)
    if key in table:
        return table[key]
    all_routes = compiler.routes(source, target)
    assert all_routes, f"{value!r} has no selected route to {target.category!r}"
    image = _apply_route(value, all_routes[0])
    table[key] = image
    for other in all_routes[1:]:
        if _apply_route(value, other) is image:
            continue
        raise compiler.StructuralImageMismatch(
            f"{value!r}: the route {_route_name(all_routes[0])} and the route {_route_name(other)} "
            f"produce distinct images in {target.category!r}"
        )
    return image


def _transport_argument(argument: Any, argument_role: ArgumentRole, owner: Category) -> Any:
    # ``argument`` is whatever the caller passed to the inherited method (D13 decides its
    # role at runtime); it is returned unchanged unless it is an owned value with a route.
    # A ``candidate`` (``__eq__``, ``__contains__``) is transported by its own role when it
    # is such a value: ``x in P := U(x) in U(P)`` (D18).
    by_own_role = argument_role is ArgumentRole.POINT or argument_role is ArgumentRole.CANDIDATE
    role = role_of(argument) if by_own_role else Signature.transported_role(argument_role)
    if role is None or role_of(argument) is not role:
        return argument
    target = compiler.node(owner, role)
    source = placement_node(argument)
    if not any(compiler.same_node(target, found) for found in compiler.reachable(source)):
        return argument
    return transport(argument, target)


class ForwardedMethod:
    """A method inherited along a selected route; ``__get__`` binds the transport."""

    def __init__(self, entry: compiler.Entry) -> None:
        self._entry = entry
        self._target = compiler.Node(entry.owner, entry.role)
        declaration = f"{entry.owner!r}.{entry.role.value}.{entry.name}"
        self._signature = declared_signature(entry.function, declaration, entry.owner.local_role_class(entry.role))
        self._python_signature = inspect.signature(entry.function)

    def entry(self) -> compiler.Entry:
        return self._entry

    def __get__(self, instance: CategoryPoint | None, owner: type) -> Callable[..., Any] | ForwardedMethod:
        if instance is None:
            return self
        function = self._entry.function
        target = self._target
        roles = self._signature.parameters()
        python_signature = self._python_signature

        def bound(*arguments: Any, **keyword_arguments: Any) -> Any:
            receiver = transport(instance, target)
            call = python_signature.bind(receiver, *arguments, **keyword_arguments)
            for name, value in list(call.arguments.items())[1:]:
                parameter = python_signature.parameters[name]
                if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                    call.arguments[name] = tuple(_transport_argument(item, roles[name], target.category) for item in value)
                elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
                    call.arguments[name] = {key: _transport_argument(item, roles[name], target.category) for key, item in value.items()}
                else:
                    call.arguments[name] = _transport_argument(value, roles[name], target.category)
            return function(*call.args, **call.kwargs)

        return bound


class ForwardedObjectMethod(ForwardedMethod):
    """An inherited method whose receiver is an object."""


class ForwardedElementMethod(ForwardedMethod):
    """An inherited method whose receiver is a generalized element."""


class ForwardedMorphismMethod(ForwardedMethod):
    """An inherited method whose receiver is a morphism."""


def forwarding_descriptor(entry: compiler.Entry) -> ForwardedMethod:
    match entry.role:
        case Role.OBJECT:
            return ForwardedObjectMethod(entry)
        case Role.ELEMENT:
            return ForwardedElementMethod(entry)
        case Role.MORPHISM:
            return ForwardedMorphismMethod(entry)
    raise AssertionError(entry.role)
