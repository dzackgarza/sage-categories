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

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.descriptors import placement_node
from sage_categories.kernel.roles import CategoryPoint, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = ["is_placed", "place", "refine"]


def is_placed(candidate: Any, category: Category) -> bool:
    """Whether ``candidate`` is an object of ``category`` by established placement."""
    if role_of(candidate) is None:
        return False
    target = compiler.node(category, Role.OBJECT)
    return any(compiler.same_node(target, found) for found in compiler.reachable(placement_node(candidate)))


def place(value: CategoryPoint, category: Category) -> None:
    """Record that ``value`` was constructed as an object of ``category``."""
    value._category = category
    value.__class__ = compiler.node(category, Role.OBJECT).category.role_class(compiler.node(category, Role.OBJECT).role)


def _is_subcategory(inner: Category, outer: Category) -> bool:
    outer_node = compiler.node(outer, Role.OBJECT)
    return any(compiler.same_node(outer_node, found) for found in compiler.reachable(compiler.node(inner, Role.OBJECT)))


def _join(current: Category, target: Category) -> Category:
    """The intersection of two placements: the narrower base, narrowed by both root sets."""
    if _is_subcategory(target, current):
        return target
    current_base, target_base = current.narrowing_base(), target.narrowing_base()
    base = current_base if _is_subcategory(current_base, target_base) else target_base
    return base.intersection((*current.narrowing_roots(), *target.narrowing_roots()))


def refine(value: CategoryPoint, target: Category) -> None:
    """Refine ``value`` in place into the subcategory ``target`` (POL-KERNEL-012)."""
    if is_placed(value, target):
        return
    assert role_of(value) in (Role.OBJECT, Role.MORPHISM), f"{value!r} is not refinable in this unit"
    place(value, _join(value.category(), target))
