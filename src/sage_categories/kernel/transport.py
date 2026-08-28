"""Canonical structural inputs through functor-owned conversions.

Selected functors supply the object, element, and morphism construction-input
conversions.  This module composes those conversions along complete structural
routes and checks diamonds by their constructor data, never by their public
images (POL-CAT-061/066/071, POL-FUN-003/035; ``specs/resolution.md``,
"Constructor agreement and functor images").  It never participates in inherited
method dispatch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, overload

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.caches import canonical_input, has_canonical_transport, retain_canonical_transport
from sage_categories.kernel.roles import CategoryPoint, ElementOfObject, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.kernel.construction import ElementConstructionInput, MorphismConstructionInput, ObjectConstructionInput

__all__ = ["construction_input", "placement_node", "role_node"]


def placement_node(value: CategoryPoint) -> compiler.Node:
    """The narrowest node ``value`` is an object of: the node its placement category names."""
    match role_of(value):
        case Role.OBJECT | Role.MORPHISM:
            return compiler.node(value.category(), Role.OBJECT)
        case Role.ELEMENT:
            return compiler.node(value.parent().category(), Role.ELEMENT)
    raise AssertionError(f"{value!r} is not an owned value")


def role_node(value: CategoryPoint) -> compiler.Node:
    """The node of ``value`` in its own role: where a structural route out of it starts.

    A morphism's placement can be a narrowing of ``Mor(C)`` -- a fixed-endpoint category
    or a property subcategory -- and such a narrowing is the object node of its own
    category, not a morphism node (``kernel/compiler.py``, ``_kernel_chain``).  The
    morphism role it lives in is ``(C, morphism)``, the node its placement narrows, which
    ``Category.base_category`` names.  Placement and role are two facts about one value
    and neither replaces the other (POL-CAT-076).
    """
    match role_of(value):
        case Role.OBJECT:
            return compiler.node(value.category(), Role.OBJECT)
        case Role.MORPHISM:
            return compiler.node(value.base_category(), Role.MORPHISM)
        case Role.ELEMENT:
            return compiler.node(value.parent().category(), Role.ELEMENT)
    raise AssertionError(f"{value!r} is not an owned value")


def _route_name(route: compiler.Route) -> str:
    return " then ".join(repr(step.functor) for step in route) or "the identity route"


def _from_construction(placement: Category, constructed_in: Category) -> bool:
    """Whether ``placement`` is the category a value was constructed in, or a refinement of it.

    Refinement narrows a value's placement in place and keeps its retained construction
    input, so the two agree only up to that narrowing (``kernel/refinement.py``).
    """
    from sage_categories.kernel.refinement import is_subcategory

    return is_subcategory(placement, constructed_in)


def _routes(source: compiler.Node, target: compiler.Node) -> tuple[compiler.Route, ...]:
    assert source.role is target.role
    routes = compiler.routes(source, target)
    assert routes, f"{source.category!r} has no selected route to {target.category!r}"
    return routes


def _object_route[
    SourceValue: ObjectOfCategory,
    SourceDatum,
    TargetValue: ObjectOfCategory,
    TargetDatum,
](
    source: ObjectConstructionInput[SourceValue, SourceDatum],
    route: compiler.Route,
) -> ObjectConstructionInput[TargetValue, TargetDatum]:
    current = source
    for step in route:
        # A selected route keeps its role: a level shift changes it and ends in the
        # element role, so it never occurs on a route between two object nodes.
        assert step.source_role is Role.OBJECT and step.functor is not None
        current = step.functor.object_constructor_input(current)
    return current


def _element_route[
    SourceValue: CategoryPoint,
    SourceDatum,
    TargetValue: CategoryPoint,
    TargetDatum,
](
    source: ElementConstructionInput[SourceValue, SourceDatum],
    route: compiler.Route,
) -> ElementConstructionInput[TargetValue, TargetDatum]:
    current = source
    for step in route:
        # A selected route keeps its role: a level shift changes it and ends in the
        # element role, so it never occurs on a route between two element nodes.
        assert step.source_role is Role.ELEMENT and step.functor is not None
        current = step.functor.element_constructor_input(current)
    return current


def _morphism_route[
    SourceValue: MorphismOfCategory,
    SourceDatum,
    TargetValue: MorphismOfCategory,
    TargetDatum,
](
    source: MorphismConstructionInput[SourceValue, SourceDatum],
    route: compiler.Route,
) -> MorphismConstructionInput[TargetValue, TargetDatum]:
    current = source
    for step in route:
        # A selected route keeps its role: a level shift changes it and ends in the
        # element role, so it never occurs on a route between two morphism nodes.
        assert step.source_role is Role.MORPHISM and step.functor is not None
        current = step.functor.morphism_constructor_input(current)
    return current


def _disagree(first: object, second: object) -> bool:
    """Whether two routes decidedly supply different constructor data (``specs/resolution.md``, final decision 4)."""
    from sage_categories.kernel.predicates import ask

    return ask(first == second) is False


def _raise_mismatch(routes: tuple[compiler.Route, ...], route: compiler.Route, target: compiler.Node) -> None:
    raise compiler.ConstructorDataMismatch(
        f"the route {_route_name(routes[0])} and the route {_route_name(route)} "
        f"supply distinct constructor data in {target.category!r}"
    )


def _object_input_at[
    SourceValue: ObjectOfCategory,
    SourceDatum,
    TargetValue: ObjectOfCategory,
    TargetDatum,
](
    source: ObjectConstructionInput[SourceValue, SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> ObjectConstructionInput[TargetValue, TargetDatum]:
    assert _from_construction(source_node.category, source.identity.category), (
        f"{source.canonical_image!r} is placed in {source_node.category!r}, which is not the category "
        f"{source.identity.category!r} it was constructed in or a refinement of it"
    )
    routes = _routes(source_node, target)
    first = _object_route(source, routes[0])
    for route in routes[1:]:
        candidate = _object_route(source, route)
        if _disagree(candidate.datum, first.datum):
            _raise_mismatch(routes, route, target)
    return first


def _element_input_at[
    SourceValue: CategoryPoint,
    SourceDatum,
    TargetValue: CategoryPoint,
    TargetDatum,
](
    source: ElementConstructionInput[SourceValue, SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> ElementConstructionInput[TargetValue, TargetDatum]:
    from sage_categories.kernel.construction import ElementRoleIdentity

    assert isinstance(source.identity, ElementRoleIdentity)
    category = source.identity.defining_morphism.codomain().category()
    assert _from_construction(source_node.category, category), (
        f"{source.canonical_image!r} is placed in {source_node.category!r}, which is not the category "
        f"{category!r} of its parent or a refinement of it"
    )
    routes = _routes(source_node, target)
    first = _element_route(source, routes[0])
    for route in routes[1:]:
        candidate = _element_route(source, route)
        if _disagree(candidate.datum, first.datum):
            _raise_mismatch(routes, route, target)
    return first


def _morphism_input_at[
    SourceValue: MorphismOfCategory,
    SourceDatum,
    TargetValue: MorphismOfCategory,
    TargetDatum,
](
    source: MorphismConstructionInput[SourceValue, SourceDatum],
    source_node: compiler.Node,
    target: compiler.Node,
) -> MorphismConstructionInput[TargetValue, TargetDatum]:
    assert _from_construction(source_node.category, source.identity.category), (
        f"{source.canonical_image!r} is placed in {source_node.category!r}, which is not the category "
        f"{source.identity.category!r} it was constructed in or a refinement of it"
    )
    routes = _routes(source_node, target)
    first = _morphism_route(source, routes[0])
    for route in routes[1:]:
        candidate = _morphism_route(source, route)
        if _disagree(candidate.datum, first.datum):
            _raise_mismatch(routes, route, target)
    return first


@overload
def construction_input[TargetValue: ObjectOfCategory, Datum](
    value: ObjectOfCategory,
    target: compiler.Node,
) -> ObjectConstructionInput[TargetValue, Datum]: ...


@overload
def construction_input[TargetValue: ElementOfObject, Datum](
    value: ElementOfObject,
    target: compiler.Node,
) -> ElementConstructionInput[TargetValue, Datum]: ...


@overload
def construction_input[TargetValue: MorphismOfCategory, Datum](
    value: MorphismOfCategory,
    target: compiler.Node,
) -> MorphismConstructionInput[TargetValue, Datum]: ...


@overload
def construction_input[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    value: CategoryPoint,
    target: compiler.Node,
) -> ObjectConstructionInput[ObjectValue, Datum] | ElementConstructionInput[ElementValue, Datum] | MorphismConstructionInput[MorphismValue, Datum]: ...


def construction_input[
    ObjectValue: ObjectOfCategory,
    ElementValue: CategoryPoint,
    MorphismValue: MorphismOfCategory,
    Datum,
](
    value: CategoryPoint,
    target: compiler.Node,
) -> ObjectConstructionInput[ObjectValue, Datum] | ElementConstructionInput[ElementValue, Datum] | MorphismConstructionInput[MorphismValue, Datum]:
    """The retained input for the canonical image of ``value`` at ``target``."""
    if has_canonical_transport(value, target.category):
        return canonical_input(value, target.category)
    source = role_node(value)
    assert source.role is target.role

    match role_of(value):
        case Role.OBJECT:
            from sage_categories.kernel.construction import retained_object_input

            assert isinstance(value, ObjectOfCategory)
            root = retained_object_input(value)
            converted = root if compiler.same_node(source, target) else _object_input_at(root, source, target)
        case Role.ELEMENT:
            from sage_categories.kernel.construction import retained_element_input

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
