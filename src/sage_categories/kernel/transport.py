"""Canonical structural inputs through functor-owned conversions.

Selected functors supply the object, element, and morphism construction-input
conversions.  This module composes those conversions along complete structural
routes and checks diamonds by image and input identity (POL-CAT-061/066/071,
POL-FUN-003/035).  It never participates in inherited method dispatch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.caches import canonical_input, has_canonical_transport, retain_canonical_transport
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.kernel.construction import ElementConstructionInput, MorphismConstructionInput, ObjectConstructionInput

__all__ = ["construction_input", "placement_node"]


def placement_node(value: CategoryPoint) -> compiler.Node:
    """The normalized role node in which ``value`` currently lives."""
    match role_of(value):
        case Role.OBJECT | Role.MORPHISM:
            return compiler.node(value.category(), Role.OBJECT)
        case Role.ELEMENT:
            assert isinstance(value, ElementOfObject)
            return compiler.node(value.parent().category(), Role.ELEMENT)
    raise AssertionError(f"{value!r} is not an owned value")


def _route_name(route: compiler.Route) -> str:
    return " then ".join(repr(functor) for functor, _ in route) or "the identity route"


def _routes(source: compiler.Node, target: compiler.Node) -> tuple[compiler.Route, ...]:
    assert source.role is target.role
    routes = compiler.routes(source, target)
    assert routes, f"{source.category!r} has no selected route to {target.category!r}"
    return routes


def _object_route[SourceDatum, TargetDatum](
    source: ObjectConstructionInput[SourceDatum],
    route: compiler.Route,
) -> ObjectConstructionInput[TargetDatum]:
    current = source
    for functor, role in route:
        assert role is Role.OBJECT
        current = functor.object_constructor_input(current)
    return current


def _element_route[SourceDatum, TargetDatum](
    source: ElementConstructionInput[SourceDatum],
    route: compiler.Route,
) -> ElementConstructionInput[TargetDatum]:
    current = source
    for functor, role in route:
        assert role is Role.ELEMENT
        current = functor.element_constructor_input(current)
    return current


def _morphism_route[SourceDatum, TargetDatum](
    source: MorphismConstructionInput[SourceDatum],
    route: compiler.Route,
) -> MorphismConstructionInput[TargetDatum]:
    current = source
    for functor, role in route:
        assert role is Role.MORPHISM
        current = functor.morphism_constructor_input(current)
    return current


def _raise_mismatch(routes: tuple[compiler.Route, ...], route: compiler.Route, target: compiler.Node) -> None:
    raise compiler.StructuralImageMismatch(
        f"the route {_route_name(routes[0])} and the route {_route_name(route)} "
        f"produce distinct construction inputs or images in {target.category!r}"
    )


def _object_input_at[SourceDatum, TargetDatum](
    source: ObjectConstructionInput[SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> ObjectConstructionInput[TargetDatum]:
    assert compiler.same_node(compiler.node(source.identity.category, Role.OBJECT), source_node)
    routes = _routes(source_node, target)
    first = _object_route(source, routes[0])
    for route in routes[1:]:
        candidate = _object_route(source, route)
        if candidate is not first or candidate.canonical_image is not first.canonical_image:
            _raise_mismatch(routes, route, target)
    return first


def _element_input_at[SourceDatum, TargetDatum](
    source: ElementConstructionInput[SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> ElementConstructionInput[TargetDatum]:
    category = source.identity.defining_morphism.codomain().category()
    assert compiler.same_node(compiler.node(category, Role.ELEMENT), source_node)
    routes = _routes(source_node, target)
    first = _element_route(source, routes[0])
    for route in routes[1:]:
        candidate = _element_route(source, route)
        if candidate is not first or candidate.canonical_image is not first.canonical_image:
            _raise_mismatch(routes, route, target)
    return first


def _morphism_input_at[SourceDatum, TargetDatum](
    source: MorphismConstructionInput[SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> MorphismConstructionInput[TargetDatum]:
    assert compiler.same_node(compiler.node(source.identity.category, Role.OBJECT), source_node)
    routes = _routes(source_node, target)
    first = _morphism_route(source, routes[0])
    for route in routes[1:]:
        candidate = _morphism_route(source, route)
        if candidate is not first or candidate.canonical_image is not first.canonical_image:
            _raise_mismatch(routes, route, target)
    return first


@overload
def construction_input[Datum](value: ObjectOfCategory, target: compiler.Node) -> ObjectConstructionInput[Datum]: ...


@overload
def construction_input[Datum](value: ElementOfObject, target: compiler.Node) -> ElementConstructionInput[Datum]: ...


@overload
def construction_input[Datum](value: MorphismOfCategory, target: compiler.Node) -> MorphismConstructionInput[Datum]: ...


def construction_input[Datum](
    value: CategoryPoint,
    target: compiler.Node,
) -> ObjectConstructionInput[Datum] | ElementConstructionInput[Datum] | MorphismConstructionInput[Datum]:
    """The retained input for the canonical image of ``value`` at ``target``."""
    source = placement_node(value)
    assert source.role is target.role
    if has_canonical_transport(value, target.category):
        return canonical_input(value, target.category)

    match role_of(value):
        case Role.OBJECT:
            from sage_categories.kernel.construction import retained_object_input

            assert isinstance(value, ObjectOfCategory)
            root = retained_object_input(value)
            converted = root if compiler.same_node(source, target) else _object_input_at(root, source, target)
        case Role.ELEMENT:
            from sage_categories.kernel.construction import retained_element_input

            assert isinstance(value, ElementOfObject)
            root = retained_element_input(value)
            converted = root if compiler.same_node(source, target) else _element_input_at(root, source, target)
        case Role.MORPHISM:
            from sage_categories.kernel.construction import retained_morphism_input

            assert isinstance(value, MorphismOfCategory)
            root = retained_morphism_input(value)
            converted = root if compiler.same_node(source, target) else _morphism_input_at(root, source, target)
        case _:
            raise AssertionError(f"{value!r} is not an owned value")

    retain_canonical_transport(value, target.category, converted.canonical_image, converted)
    return converted
