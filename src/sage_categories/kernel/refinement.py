"""Placement and same-object property refinement (POL-KERNEL-002/013/014).

``is_placed(x, C)`` is the implementation fact "``x`` entered ``C`` or a selected
subcategory of ``C``" (POL-CAT-068): the node of ``C`` is reachable from ``x``'s
placement node through selected inclusions, which is also how every recorded
implication between property categories acts (D09).

``refine(x, P)`` strengthens ``x``'s placement to the join of its current category
with the property category ``P``, rebuilding its dynamic class in place.  Identity,
construction data, and existing canonical images are preserved; no wrapper or
second value is allocated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sage.structure.dynamic_class import dynamic_class

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.descriptors import placement_node
from sage_categories.kernel.roles import CategoryPoint, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["is_placed", "is_subcategory", "place", "refine"]


def is_placed(candidate: Any, category: Category) -> bool:
    """Whether ``candidate`` is an object of ``category`` by established placement."""
    if role_of(candidate) is None:
        return False
    target = compiler.node(category, Role.OBJECT)
    return any(compiler.same_node(target, found) for found in compiler.reachable(placement_node(candidate)))


def place(value: CategoryPoint, category: Category) -> None:
    """Record that ``value`` was constructed as an object of ``category``.

    The value keeps its own implementation class: an object of ``Cat()`` is an
    instance of its own ``Category`` subclass, so its refined class is the join of
    the target role class with that class (POL-KERNEL-013, POL-CAT-074).
    """
    target = compiler.node(category, Role.OBJECT)
    role_class = target.category.role_class(target.role)
    value._category = category
    if issubclass(type(value), role_class):
        return
    if issubclass(role_class, type(value)):
        value.__class__ = role_class
        return
    value.__class__ = dynamic_class(role_class.__name__, (role_class, type(value)), prepend_cls_bases=False)


def is_subcategory(inner: Category, outer: Category) -> bool:
    """Whether ``outer`` is reachable from ``inner`` through selected functors on objects."""
    outer_node = compiler.node(outer, Role.OBJECT)
    return any(compiler.same_node(outer_node, found) for found in compiler.reachable(compiler.node(inner, Role.OBJECT)))


def _join(current: Category, target: Category) -> Category:
    """The intersection of two placements: the narrower base, narrowed by both root sets."""
    if is_subcategory(target, current):
        return target
    current_base, target_base = current.narrowing_base(), target.narrowing_base()
    base = current_base if is_subcategory(current_base, target_base) else target_base
    return base.intersection((*current.narrowing_roots(), *target.narrowing_roots()))


def refine(value: CategoryPoint, target: Category) -> None:
    """Refine ``value`` in place into the subcategory ``target`` (POL-KERNEL-012)."""
    if is_placed(value, target):
        return
    assert role_of(value) in (Role.OBJECT, Role.MORPHISM), f"{value!r} is not refinable in this unit"
    place(value, _join(value.category(), target))
