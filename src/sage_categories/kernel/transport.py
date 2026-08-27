"""Canonical structural images through functor-owned constructor conversions.

Selected functors supply the object, element, and morphism construction-input
conversions.  This module composes those conversions along complete structural
routes and checks diamonds by image and input identity (POL-CAT-061/066/071,
POL-FUN-003/035).  It never participates in inherited method dispatch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.caches import (
    canonical_image,
    canonical_input,
    has_canonical_transport,
    retain_canonical_transport,
)
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.kernel.construction import ElementConstruction, MorphismConstruction, ObjectConstruction

__all__ = ["construction_input", "convert_construction_input", "placement_node", "transport"]


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


@overload
def _apply_route(source: ObjectConstruction, route: compiler.Route, role: Role) -> ObjectConstruction: ...


@overload
def _apply_route(source: ElementConstruction, route: compiler.Route, role: Role) -> ElementConstruction: ...


@overload
def _apply_route(source: MorphismConstruction, route: compiler.Route, role: Role) -> MorphismConstruction: ...


def _apply_route(
    source: ObjectConstruction | ElementConstruction | MorphismConstruction,
    route: compiler.Route,
    role: Role,
) -> ObjectConstruction | ElementConstruction | MorphismConstruction:
    current = source
    for functor, step_role in route:
        assert step_role is role
        match role:
            case Role.OBJECT:
                current = functor.object_constructor_input(current)
            case Role.ELEMENT:
                current = functor.element_constructor_input(current)
            case Role.MORPHISM:
                current = functor.morphism_constructor_input(current)
    return current


@overload
def convert_construction_input(
    source: ObjectConstruction,
    source_node: compiler.Node,
    target: compiler.Node,
) -> ObjectConstruction: ...


@overload
def convert_construction_input(
    source: ElementConstruction,
    source_node: compiler.Node,
    target: compiler.Node,
) -> ElementConstruction: ...


@overload
def convert_construction_input(
    source: MorphismConstruction,
    source_node: compiler.Node,
    target: compiler.Node,
) -> MorphismConstruction: ...


def convert_construction_input(
    source: ObjectConstruction | ElementConstruction | MorphismConstruction,
    source_node: compiler.Node,
    target: compiler.Node,
) -> ObjectConstruction | ElementConstruction | MorphismConstruction:
    """Convert one complete input to ``target`` through every selected route.

    This is the pre-initialization boundary.  It reads only the supplied input and
    functor conversions.  It does not inspect the allocated source value.
    """
    input_role = Role.OBJECT if source_node.role is Role.MORPHISM else source_node.role
    assert compiler.same_node(compiler.node(source.category, input_role), source_node)
    assert source_node.role is target.role
    all_routes = compiler.routes(source_node, target)
    assert all_routes, f"{source_node.category!r} has no selected route to {target.category!r}"
    first = _apply_route(source, all_routes[0], source_node.role)
    for route in all_routes[1:]:
        candidate = _apply_route(source, route, source_node.role)
        if candidate is first and candidate.canonical_image is first.canonical_image:
            continue
        raise compiler.StructuralImageMismatch(
            f"the route {_route_name(all_routes[0])} and the route {_route_name(route)} "
            f"produce distinct construction inputs or images in {target.category!r}"
        )
    return first


@overload
def _input_of(value: ObjectOfCategory) -> ObjectConstruction: ...


@overload
def _input_of(value: ElementOfObject) -> ElementConstruction: ...


@overload
def _input_of(value: MorphismOfCategory) -> MorphismConstruction: ...


def _input_of(
    value: CategoryPoint,
) -> ObjectConstruction | ElementConstruction | MorphismConstruction:
    match role_of(value):
        case Role.OBJECT:
            from sage_categories.kernel.construction import input_of_object

            assert isinstance(value, ObjectOfCategory)
            return input_of_object(value)
        case Role.ELEMENT:
            from sage_categories.kernel.construction import input_of_element

            assert isinstance(value, ElementOfObject)
            return input_of_element(value)
        case Role.MORPHISM:
            from sage_categories.kernel.construction import input_of_morphism

            assert isinstance(value, MorphismOfCategory)
            return input_of_morphism(value)
    raise AssertionError(f"{value!r} is not an owned value")


@overload
def construction_input(value: ObjectOfCategory, target: compiler.Node) -> ObjectConstruction: ...


@overload
def construction_input(value: ElementOfObject, target: compiler.Node) -> ElementConstruction: ...


@overload
def construction_input(value: MorphismOfCategory, target: compiler.Node) -> MorphismConstruction: ...


def construction_input(
    value: CategoryPoint,
    target: compiler.Node,
) -> ObjectConstruction | ElementConstruction | MorphismConstruction:
    """The retained input for the canonical image of ``value`` at ``target``."""
    source = placement_node(value)
    assert source.role is target.role
    if compiler.same_node(source, target):
        return _input_of(value)
    if has_canonical_transport(value, target.category):
        return canonical_input(value, target.category)
    converted = convert_construction_input(_input_of(value), source, target)
    retain_canonical_transport(value, target.category, converted.canonical_image, converted)
    return converted


@overload
def transport(value: ObjectOfCategory, target: compiler.Node) -> ObjectOfCategory: ...


@overload
def transport(value: ElementOfObject, target: compiler.Node) -> ElementOfObject: ...


@overload
def transport(value: MorphismOfCategory, target: compiler.Node) -> MorphismOfCategory: ...


def transport(value: CategoryPoint, target: compiler.Node) -> CategoryPoint:
    """The canonical public functor image of ``value`` at ``target``."""
    source = placement_node(value)
    if compiler.same_node(source, target):
        return value
    if has_canonical_transport(value, target.category):
        return canonical_image(value, target.category)
    return construction_input(value, target).canonical_image
