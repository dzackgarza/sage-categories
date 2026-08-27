"""Placement and same-object property refinement (POL-KERNEL-002/013/014).

``is_placed(x, C)`` is the implementation fact "``x`` entered ``C`` or a declared
subcategory of ``C``" (POL-CAT-068): the node of ``C`` is reachable from ``x``'s
placement node through retained inclusions alone (POL-FUN-027).  A selected functor that
is not the retained inclusion of its endpoints changes structure and places
nothing: an object of a category with a selected forgetful functor ``U: C -> D``
is not an object of ``D``.  Every recorded implication between property
categories is such an inclusion, so implications act through the same walk (POL-FUN-024).

``refine(x, P)`` strengthens ``x``'s placement to the join of its current category
with the property category ``P``, rebuilding its dynamic class in place.  Identity,
construction data, and existing canonical images are preserved; no wrapper or
second value is allocated.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from sage.structure.dynamic_class import dynamic_class

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, Role, role_of
from sage_categories.kernel.transport import placement_node

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["common_ancestor", "is_placed", "is_retained_inclusion", "is_subcategory", "place", "refine"]


def is_retained_inclusion(functor: MorphismOfCategory) -> bool:
    """Whether ``functor`` is the inclusion that ``Fun`` retained for its endpoints (POL-FUN-027)."""
    functors = functor.base_category().morphism_category(1)
    source, target = functor.domain(), functor.codomain()
    return functors.retains_inclusion(source, target) and functors.inclusion_of(source, target) is functor


def _included_in(start: compiler.Node) -> Iterator[compiler.Node]:
    """Every node reachable from ``start`` through retained inclusions, ``start`` first."""
    found: list[compiler.Node] = [start]
    frontier = [start]
    while frontier:
        current = frontier.pop(0)
        yield current
        for functor in current.category.selected_functors():
            if not is_retained_inclusion(functor):
                continue
            target = compiler.node(functor.codomain(), current.role)
            if any(compiler.same_node(target, known) for known in found):
                continue
            found.append(target)
            frontier.append(target)


def is_placed(candidate: Any, category: Category) -> bool:
    """Whether ``candidate`` is an object of ``category`` by established placement (the ``member`` handler; POL-TYPE-004)."""
    if role_of(candidate) is None:
        return False
    target = compiler.node(category, Role.OBJECT)
    return any(compiler.same_node(target, found) for found in _included_in(placement_node(candidate)))


def is_subcategory(inner: Category, outer: Category) -> bool:
    """Whether ``inner`` is ``outer`` or a declared subcategory of it, through retained inclusions."""
    outer_node = compiler.node(outer, Role.OBJECT)
    return any(compiler.same_node(outer_node, found) for found in _included_in(compiler.node(inner, Role.OBJECT)))


def common_ancestor(first: Category, second: Category) -> Category:
    """The least category receiving both, along retained inclusions (POL-CAT-088, POL-FUN-027).

    ``_included_in`` walks the inclusion order breadth first, so the first category
    receiving ``first`` that also receives ``second`` is minimal among the categories
    receiving both.  A selected functor that is not a retained inclusion changes
    structure and is not walked, so a poset and a set meet nowhere.
    """
    found = next(
        (
            reached.category
            for reached in _included_in(compiler.node(first, Role.OBJECT))
            if is_subcategory(second, reached.category)
        ),
        None,
    )
    assert found is not None, f"{first!r} and {second!r} have no least common category along retained inclusions"
    return found


def place(value: CategoryPoint, category: Category) -> None:
    """Record that ``value`` was constructed as an object of ``category``.

    The value keeps its own implementation class: an object of ``Cat()`` is an
    instance of its own ``Category`` subclass, so its refined class is the join of
    that class with the target role class (POL-KERNEL-013, POL-CAT-074).

    The value's own class comes first.  It declares the mathematics this one value
    owns; the role class supplies what every value of the category inherits, so the
    declaration overrides the inherited method rather than the reverse.  This is
    Sage's ``Parent._init_category_`` and ``Parent._refine_category_``, which build
    ``dynamic_class(f"{type(self).__name__}_with_category", (type(self),
    category.parent_class), doccls=type(self))`` (``sage/structure/parent.pyx``,
    inspected 2026-08-27).  ``Cat()`` is the value that needs it: its declaration
    ``CategoryOfCategories`` names the morphism and two-morphism types of ``Cat``,
    while the compiled ``Cat().ObjectType`` carries the generic
    ``CategoryDeclaration`` body every category inherits.
    """
    target = compiler.node(category, Role.OBJECT)
    role_class = target.category.role_class(target.role)
    value._category = category
    match role_of(value):
        case Role.OBJECT:
            from sage_categories.kernel.construction import ObjectStageIdentity

            value._cat_element_identity = ObjectStageIdentity(category)
        case Role.MORPHISM:
            from sage_categories.kernel.construction import ArrowStageIdentity

            value._cat_element_identity = ArrowStageIdentity(category.base_category(), value.domain(), value.codomain())
    if issubclass(type(value), role_class):
        return
    if issubclass(role_class, type(value)):
        value.__class__ = role_class
        return
    declared = type(value)
    value.__class__ = dynamic_class(
        f"{declared.__name__}_with_category",
        (declared, role_class),
        doccls=declared,
        prepend_cls_bases=False,
    )


def _join(current: Category, target: Category) -> Category:
    """The intersection of two placements: the narrower base, narrowed by both root sets."""
    if is_subcategory(target, current):
        return target
    current_base, target_base = current.narrowing_base(), target.narrowing_base()
    if is_subcategory(current_base, target_base):
        base = current_base
    else:
        # A placement is never weakened to reach a property (POL-CAT-074): the two
        # bases must be comparable so that the join is a narrowing of the finer one.
        assert is_subcategory(target_base, current_base), (
            f"{current!r} and {target!r} have no common placement: {current_base!r} and {target_base!r} are incomparable"
        )
        base = target_base
    return base.intersection((*current.narrowing_roots(), *target.narrowing_roots()))


def refine(value: CategoryPoint, target: Category) -> None:
    """Refine ``value`` in place into the subcategory ``target`` (POL-KERNEL-012)."""
    if is_placed(value, target):
        return
    assert role_of(value) in (Role.OBJECT, Role.MORPHISM), f"{value!r} is not refinable: only objects and morphisms are placed"
    place(value, _join(value.category(), target))
