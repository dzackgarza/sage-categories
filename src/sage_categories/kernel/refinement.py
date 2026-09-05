"""Implement category placement and same-object property refinement."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

import sage_categories.kernel.compiler as compiler
from sage_categories.kernel.roles import (
    CategoryPoint,
    MorphismOfCategory,
    Role,
    RoleCandidate,
    is_category,
    role_of,
)

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
    "FunctorDeclarationReader",
    "common_ancestor",
    "declares_point",
    "install_functor_declaration_readers",
    "is_placed",
    "is_subcategory",
    "place",
    "refine",
    "traces_inheritance",
    "traces_placement",
]


type FunctorDeclarationReader = Callable[[MorphismOfCategory], bool]

_traces_placement: FunctorDeclarationReader | None = None
_traces_inheritance: FunctorDeclarationReader | None = None
_declares_point: FunctorDeclarationReader | None = None


def install_functor_declaration_readers(
    placement: FunctorDeclarationReader,
    inheritance: FunctorDeclarationReader,
    point: FunctorDeclarationReader,
) -> None:
    """Install ``cat_kernel``'s three readers of a functor's declared properties (D175).

    Deciding whether a functor carries placement and inheritance, or declares a point,
    reads the property subcategory the functor was constructed in, which is ``Cat``'s;
    walking the placement graph and compiling the implementation classes is the kernel's,
    and ``Cat`` calls that walk from thirteen of its own modules.  ``cat_kernel`` is the
    layer that has both, so it hands the readers down rather than the kernel reaching up
    (``specs/resolution.md``, "The closed kernel surface").
    """
    global _traces_placement, _traces_inheritance, _declares_point
    _traces_placement, _traces_inheritance, _declares_point = placement, inheritance, point


def traces_placement(functor: MorphismOfCategory) -> bool:
    """Whether placement follows ``functor``: it is declared a monomorphism of ``Cat()`` and an isofibration (POL-FUN-036)."""
    assert _traces_placement is not None, "cat_kernel installs the functor declaration readers before any category is declared"
    return _traces_placement(functor)


def traces_inheritance(functor: MorphismOfCategory) -> bool:
    """Whether inheritance follows ``functor``: it is declared an isofibration (D164 to D167)."""
    assert _traces_inheritance is not None, "cat_kernel installs the functor declaration readers before any category is declared"
    return _traces_inheritance(functor)


def declares_point(functor: MorphismOfCategory) -> bool:
    """Whether ``functor`` is declared a point ``* -> C``, the arrow that places its object in ``C`` (D154, D162)."""
    assert _declares_point is not None, "cat_kernel installs the functor declaration readers before any category is declared"
    return _declares_point(functor)


def _reached_placements(start: compiler.Node) -> Iterator[compiler.Node]:
    """Every node reachable from ``start`` through placement-tracing functors, ``start`` first."""
    found: list[compiler.Node] = [start]
    frontier = [start]
    while frontier:
        current = frontier.pop(0)
        yield current
        for functor in current.category.selected_functors():
            if not traces_placement(functor):
                continue
            target = compiler.node(functor.codomain(), current.role)
            if any(compiler.same_node(target, known) for known in found):
                continue
            found.append(target)
            frontier.append(target)


def _reached_subcategories(start: Category) -> Iterator[Category]:
    """Every exact category reached through placement-tracing functors."""
    found: list[Category] = [start]
    frontier = [start]
    while frontier:
        current = frontier.pop(0)
        yield current
        for functor in current.selected_functors():
            if not traces_placement(functor):
                continue
            target = functor.codomain()
            if any(target is known for known in found):
                continue
            found.append(target)
            frontier.append(target)


def _placement_node(value: CategoryPoint) -> compiler.Node:
    """The object node named by the value's current placement."""
    match role_of(value):
        case Role.OBJECT | Role.MORPHISM:
            return compiler.node(value.category(), Role.OBJECT)
        case Role.ELEMENT:
            return compiler.node(value.parent().category(), Role.ELEMENT)
    raise AssertionError(f"{value!r} is not an owned value")


def is_placed(candidate: RoleCandidate, category: Category) -> bool:
    """Whether ``candidate`` is an object of ``category`` by established placement (the ``member`` handler; POL-TYPE-004)."""
    if role_of(candidate) is None:
        return False
    assert isinstance(candidate, CategoryPoint)
    target = compiler.node(category, Role.OBJECT)
    placements = [_placement_node(candidate)]
    if role_of(candidate) is Role.OBJECT:
        from sage_categories.kernel.construction import retained_object_input

        identity = retained_object_input(candidate).identity
        if identity.universe is not None:
            placements.append(compiler.node(identity.universe, Role.OBJECT))
    return any(
        compiler.same_node(target, found)
        for placement in placements
        for found in _reached_placements(placement)
    )


def is_subcategory(inner: Category, outer: Category) -> bool:
    """Whether ``inner`` is ``outer`` or a declared subcategory of it, through placement-tracing functors."""
    return any(found is outer for found in _reached_subcategories(inner))


def common_ancestor(first: Category, second: Category) -> Category | None:
    """The narrowest category containing both, along placement-tracing functors, or ``None`` (POL-CAT-088, POL-FUN-036).

    Narrowest is minimal in the subcategory order, not first in the walk: a category
    declares its subcategory monomorphisms in its own preference order, so the walk can
    reach a wider category before a narrower one.  A selected functor that does not trace
    placement changes structure and is not walked, so a poset and a set meet nowhere.  The
    caller states the precondition, because only the caller knows the two values.
    """
    common = [reached for reached in _reached_subcategories(first) if is_subcategory(second, reached)]
    return next((candidate for candidate in common if all(is_subcategory(candidate, other) for other in common)), None)


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
    inspected 2026-08-27).  A slice category is a value that needs it: it is an instance
    of ``SliceLikeCategory``, and the role class of the pullback placement it refines into
    carries what every pullback category inherits.
    """
    target = compiler.node(category, Role.OBJECT)
    role_class = target.category.role_class(target.role)
    value._category = category
    compiler._refine_implementation_class(value, role_class)
    if is_category(value):
        compiler.apply_level_shift(value, category)


def _join(current: Category, target: Category) -> Category:
    """The intersection of two placements: the narrower base, narrowed by both root sets."""
    current_base, target_base = current.narrowing_base(), target.narrowing_base()
    current_roots = current.narrowing_roots()
    if compiler.same_node(compiler.node(current_base, Role.OBJECT), compiler.node(target_base, Role.OBJECT)):
        base = target_base
        if current_base is not target_base and current_base.op() is target_base:
            current_roots = tuple(root.op() for root in current_roots)
    elif is_subcategory(target, current):
        return target
    elif is_subcategory(current_base, target_base):
        base = current_base
    else:
        # A placement is never weakened to reach a property (POL-CAT-074): the two
        # bases must be comparable so that the join is a narrowing of the finer one.
        assert is_subcategory(target_base, current_base), (
            f"{current!r} and {target!r} have no common placement: {current_base!r} and {target_base!r} are incomparable"
        )
        base = target_base
    return base.intersection((*current_roots, *target.narrowing_roots()))


def refine(value: CategoryPoint, target: Category) -> None:
    """Refine ``value`` in place into the subcategory ``target`` (POL-KERNEL-012)."""
    if is_placed(value, target):
        return
    assert role_of(value) in (Role.OBJECT, Role.MORPHISM), f"{value!r} is not refinable: only objects and morphisms are placed"
    place(value, _join(value.category(), target))
