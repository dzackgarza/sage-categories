"""Forwarding descriptors and structural transport (POL-CAT-012, POL-KERNEL-021, POL-CAT-047).

An inherited method means composition: ``X.f(...) := F(X).f(...)``.  The descriptor
transports the receiver and every transportable argument forward to the declaring
node, calls the declaring method on the images, and returns its value unchanged
(there is no result branch: POL-CAT-047, ``specs/resolution.md``).  A lazy family
argument is transported one item at a time (POL-CAT-065, POL-CAT-072).

Transport applies the declared action of each selected functor (``on_object``,
``on_morphism``, ``on_element``; POL-FUN-002) as the functor's own placement
realizes it: the declaration of ``Cat().MorphismType``, or a property role of
``Fun`` that refines it (none does today).  A classical element
of the source reaches the classical stage of the codomain through the stage
comparison retained by the selected functor (``specs/functor.md``, "Structural
inheritance"); the comparison is precomposed here and nowhere else.

Transport is canonical: one image per value and reachable category, stored in
the identity-keyed tables of ``kernel/caches.py``.  At the first transport of a
value to a node, every selected route to that node is traversed in declaration
order; the first image is stored and each later image must be the same object
(POL-CAT-012).  A mismatch raises ``StructuralImageMismatch`` naming the source
construction, both routes, and the shared category; nothing is repaired.

The kernel types transport by role: the image of an object is an object, of an
element an element, of a morphism a morphism, each in the target category.  A
descriptor is generic over the declaring method's call shape and result
(POL-TYPE-028): the bound callable has the parameters of the declaration without
its receiver and returns the declaration's result.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Self, overload

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.caches import canonical_images
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of
from sage_categories.kernel.signatures import ArgumentRole, ParameterRole, Signature, declared_signature

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


def _declared[**P, R](receiver: CategoryPoint, name: str, owner: Category, role: Role) -> compiler.DeclaredMethod[P, R]:
    """The method ``name`` as the receiver's own class realizes the declaration of ``owner`` in ``role``.

    The first class-body definition in the receiver's MRO below the declaring owner
    that is not a forwarded descriptor: a refinement of the declaration by the
    receiver's placement wins over the declaration itself, and a forwarded copy of
    the declaration (which would transport the receiver again) is never chosen.

    An owned value carries the owner's *compiled* class, which holds the copied
    declaration; a category carries the owner's *declared* class instead, because a
    category is an instance of its own ``Category`` subclass and not of
    ``Cat().ObjectType``.  Either one places the receiver below the owner.
    """
    below = (owner.role_class(role), owner.local_role_class(role))
    for klass in type(receiver).__mro__:
        declared = vars(klass).get(name)
        if declared is not None and issubclass(klass, below) and not isinstance(declared, ForwardedMethod):
            return declared
    raise AssertionError(f"{receiver!r} realizes no declaration of {name!r}")


def _action[**P, R](functor: Functor, name: str) -> compiler.DeclaredMethod[P, R]:
    """The declared action of a selected functor: the action its own placement realizes (POL-FUN-002, POL-KERNEL-003).

    A functor placed in a property subcategory of ``Fun`` carries that subcategory's
    compiled surface, on which the actions are forwarded copies of the declaration
    of ``Cat().MorphismType``; applying the declaration itself is what applies the
    selected functor, and an action declared by a property role of ``Fun`` would be
    chosen first.  No property role of ``Fun`` declares one today.
    """
    return _declared(functor, name, functor.base_category(), Role.MORPHISM)


def _apply(functor: Functor, step_role: Role, value: CategoryPoint) -> CategoryPoint:
    """The declared action of a selected functor on one value in the role of the step's source node.

    An object of ``Mor(C)`` is a morphism of ``C`` (POL-CAT-021): the object action
    of a functor out of ``Mor(C)`` receives a morphism value.
    """
    match step_role:
        case Role.OBJECT:
            return _action(functor, "on_object")(functor, value)
        case Role.MORPHISM:
            return _action(functor, "on_morphism")(functor, value)
        case Role.ELEMENT:
            assert isinstance(value, ElementOfObject)
            return _apply_to_element(functor, value)
    raise AssertionError(step_role)


def _is_classical(element: ElementOfObject, category: Category) -> bool:
    return any(element.stage() is stage for stage in category.classical_stages())


def _apply_to_element(functor: Functor, element: ElementOfObject) -> ElementOfObject:
    # A classical element ``t: G_C -> X`` reaches the classical stage of the codomain
    # through the stage comparison ``c: G_D -> F(G_C)`` retained by the selected
    # functor: its image is the element ``F(t) after c`` (``specs/functor.md``,
    # "Structural inheritance"; POL-CAT-062).  The identity comparison, retained when
    # ``F(G_C) is G_D``, changes nothing.
    on_element = _action(functor, "on_element")
    if not _is_classical(element, functor.domain()) or not functor.codomain().classical_stages():
        return on_element(functor, element)
    comparison = functor.stage_comparison()
    if comparison is comparison.domain().identity():
        return on_element(functor, element)
    image = _action(functor, "on_morphism")(functor, element.defining_morphism()) * comparison
    return functor.codomain().element_from_defining_morphism(image)


def _apply_route(value: CategoryPoint, route: compiler.Route) -> CategoryPoint:
    image = value
    for step in route:
        image = _shift(step, image) if step.functor is None else _apply(step.functor, step.source_role, image)
    return image


def _shift(step: compiler.Step, value: CategoryPoint) -> CategoryPoint:
    """The level shift: an object or morphism of ``C`` as a generalized element of ``C``.

    An object is the stage-``1`` element and a morphism the stage-``[1]`` one; both are
    named by the defining morphism the value already retains, so the shift applies no
    functor and constructs no image of its own (``specs/functor.md``, "The level shift").
    """
    assert value.stage() is step.stage, f"{value!r} is not a point of {step.stage!r}"
    from sage_categories.cat.category import Cat

    return Cat().Point(value.parent()).ElementType(value.defining_morphism())


def _route_name(route: compiler.Route) -> str:
    return " then ".join(repr(step.functor) for step in route) or "the identity route"


@overload
def transport(value: ObjectOfCategory, target: compiler.Node) -> ObjectOfCategory: ...


@overload
def transport(value: ElementOfObject, target: compiler.Node) -> ElementOfObject: ...


@overload
def transport(value: MorphismOfCategory, target: compiler.Node) -> MorphismOfCategory: ...


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


def _transport_value(argument: CategoryPoint, role: Role, owner: Category, name: str, declared: ArgumentRole) -> CategoryPoint:
    """The image of one declared-role argument at the owner; an argument without an exact rule is rejected (POL-CAT-071)."""
    assert role_of(argument) is role, f"the argument {name}={argument!r} is not an owned {declared.value}"
    target = compiler.node(owner, role)
    source = placement_node(argument)
    assert any(compiler.same_node(target, found) for found in compiler.reachable(source)), (
        f"the argument {name}={argument!r}, declared {declared.value}, has no selected route from {source.category!r} to {owner!r}"
    )
    return transport(argument, target)


def _transport_family(family: Iterator[CategoryPoint], parameter: ParameterRole, owner: Category, name: str) -> Iterator[CategoryPoint]:
    """A lazy family of one declared role, transported item by item as it is consumed (POL-CAT-065, POL-CAT-072)."""
    role = Signature.transported_role(parameter.role)
    assert role is not None, parameter.role
    return (_transport_value(item, role, owner, name, parameter.role) for item in family)


@overload
def _transport_argument(argument: CategoryPoint, parameter: ParameterRole, owner: Category, name: str, receiver_is_instance: bool) -> CategoryPoint: ...


@overload
def _transport_argument[V](argument: V, parameter: ParameterRole, owner: Category, name: str, receiver_is_instance: bool) -> V: ...


def _transport_argument[V](argument: V | CategoryPoint, parameter: ParameterRole, owner: Category, name: str, receiver_is_instance: bool) -> V | CategoryPoint:
    """The argument as the declaring method receives it, by its declared role (POL-KERNEL-021).

    An owned value in a transportable role is replaced by its image at the owner; a
    plain value of a declared plain role passes as it is.
    """
    declared = parameter.role
    match declared:
        case ArgumentRole.VALUE:
            return argument
        case ArgumentRole.CANDIDATE:
            # ``x in P := U(x) in U(P)``: a candidate that is an owned value with a
            # selected route is transported by its own role; any other candidate is
            # the declaring method's to judge (POL-CAT-062).
            if not isinstance(argument, CategoryPoint):
                return argument
            role = role_of(argument)
            assert role is not None
            target = compiler.node(owner, role)
            if not any(compiler.same_node(target, found) for found in compiler.reachable(placement_node(argument))):
                return argument
            return transport(argument, target)
        case ArgumentRole.RECEIVER_POINT:
            # The route acts on the receiver; a point of the receiver's own category
            # is admitted only when the receiver's image is the receiver itself.
            assert receiver_is_instance, f"the argument {name}={argument!r} is a point of the receiver's category, which the selected route does not map"
            return argument
    if parameter.admits_value and not isinstance(argument, CategoryPoint):
        return argument
    assert isinstance(argument, CategoryPoint), f"the argument {name}={argument!r} is not an owned {declared.value}"
    role = Signature.transported_role(declared)
    assert role is not None, declared
    return _transport_value(argument, role, owner, name, declared)


def _implementation[**P, R](receiver: CategoryPoint, entry: compiler.Entry[P, R]) -> compiler.DeclaredMethod[P, R]:
    """The declaring method as the receiver's own implementation class realizes it.

    An object of ``Cat()`` is an instance of its own ``Category`` subclass, which
    refines the declarations of ``Cat().ObjectType``; ``F(X).f()`` for such an image
    is that refinement, not the base declaration.
    """
    return _declared(receiver, entry.name, entry.owner, entry.role)


class ForwardedMethod[**P, R]:
    """A method inherited along a selected route; ``__get__`` binds the transport.

    ``P`` is the call shape of the declaration without its receiver and ``R`` its
    declared result (POL-TYPE-028); the bound callable has exactly that signature.
    """

    def __init__(self, entry: compiler.Entry[P, R]) -> None:
        self._entry = entry
        self._target = compiler.Node(entry.owner, entry.role)
        declaration = f"{entry.owner!r}.{entry.role.value}.{entry.name}"
        self._signature = declared_signature(entry.function, declaration, entry.owner, entry.role)
        self._python_signature = inspect.signature(entry.function)

    def entry(self) -> compiler.Entry[P, R]:
        return self._entry

    @overload
    def __get__(self, instance: None, owner: type[CategoryPoint]) -> Self: ...

    @overload
    def __get__(self, instance: CategoryPoint, owner: type[CategoryPoint]) -> Callable[P, R]: ...

    def __get__(self, instance: CategoryPoint | None, owner: type[CategoryPoint]) -> Callable[P, R] | Self:
        if instance is None:
            return self
        target = self._target
        roles = self._signature.parameters()
        python_signature = self._python_signature

        def bound(*arguments: P.args, **keyword_arguments: P.kwargs) -> R:
            receiver = transport(instance, target)
            function = _implementation(receiver, self._entry)
            call = python_signature.bind(receiver, *arguments, **keyword_arguments)
            same = receiver is instance
            for name, value in list(call.arguments.items())[1:]:
                parameter = python_signature.parameters[name]
                if Signature.is_family(roles[name].role):
                    call.arguments[name] = _transport_family(value, roles[name], target.category, name)
                elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                    call.arguments[name] = tuple(_transport_argument(item, roles[name], target.category, name, same) for item in value)
                elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
                    call.arguments[name] = {key: _transport_argument(item, roles[name], target.category, name, same) for key, item in value.items()}
                else:
                    call.arguments[name] = _transport_argument(value, roles[name], target.category, name, same)
            return function(*call.args, **call.kwargs)

        return bound


class ForwardedObjectMethod[**P, R](ForwardedMethod[P, R]):
    """An inherited method whose receiver is an object."""


class ForwardedElementMethod[**P, R](ForwardedMethod[P, R]):
    """An inherited method whose receiver is a generalized element."""


class ForwardedMorphismMethod[**P, R](ForwardedMethod[P, R]):
    """An inherited method whose receiver is a morphism."""


def forwarding_descriptor[**P, R](entry: compiler.Entry[P, R]) -> ForwardedMethod[P, R]:
    match entry.role:
        case Role.OBJECT:
            return ForwardedObjectMethod(entry)
        case Role.ELEMENT:
            return ForwardedElementMethod(entry)
        case Role.MORPHISM:
            return ForwardedMorphismMethod(entry)
    raise AssertionError(entry.role)
