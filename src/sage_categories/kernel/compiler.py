"""The method compiler: catalogues, routes, and dynamic role classes (D07, D11, D12).

The selected graph is ``structure_functors()`` alone.  Its nodes are pairs
``(category, role)``; the node ``(Mor(C), object)`` *is* the node ``(C, morphism)``
(D03: one implementation type, one value, two placements), which
``Category.role_source`` normalizes.  A route is a simple directed path of steps
``(functor, role at the step's source)``; the graph reachable from a category is a
finite DAG, asserted at compile time (D11).

Method catalogue of a node (``specs/resolution.md``):

1. a local declaration takes precedence;
2. one declaring owner reached by several routes supplies one entry whose execution
   route is the first route in declaration order;
3. comparable owners yield the most specific one;
4. incomparable owners with one spelling raise ``SemanticCollisionError``.

The compiled role class is a Sage dynamic class (``sage.structure.dynamic_class``):
bases are the local role class followed by the codomain role classes of the
selected functors, and the surface holds one forwarding descriptor per inherited
name.  Method compilation constructs no value image (D12).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, NamedTuple

from sage.structure.dynamic_class import dynamic_class

import sage_categories.kernel.descriptors as descriptors
from sage_categories.kernel.roles import CategoryPoint, Role, kernel_base

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "Entry",
    "Node",
    "Route",
    "SemanticCollisionError",
    "StructuralImageMismatch",
    "catalogue",
    "compile_category",
    "empty_local_role",
    "node",
    "reachable",
    "routes",
    "same_node",
]


class SemanticCollisionError(Exception):
    """Two incomparable owners declare one method spelling (POL-CAT-011, POL-API-011)."""


class StructuralImageMismatch(Exception):
    """Two selected routes produced distinct images of one value (POL-CAT-012)."""


class Node(NamedTuple):
    category: Category
    role: Role


type Step = tuple[Functor, Role]
type Route = tuple[Step, ...]


class Entry(NamedTuple):
    owner: Category
    role: Role
    name: str
    function: Callable[..., Any]
    route: Route


_IGNORED_NAMES = frozenset({"__init__", "__new__", "__repr__", "__init_subclass__", "__class_getitem__"})


def node(category: Category, role: Role) -> Node:
    """The normalized node: ``(Mor(C), object)`` is ``(C, morphism)``."""
    source, source_role = category.role_source(role)
    if source is category and source_role is role:
        return Node(category, role)
    return node(source, source_role)


def same_node(first: Node, second: Node) -> bool:
    return first.category is second.category and first.role is second.role


def successors(current: Node) -> tuple[tuple[Step, Node], ...]:
    return tuple(
        ((functor, current.role), node(functor.codomain(), current.role))
        for functor in current.category.selected_functors()
    )


def reachable(start: Node) -> tuple[Node, ...]:
    """Every node reachable from ``start`` (``start`` first), in breadth-first declaration order."""
    found: list[Node] = [start]
    frontier = [start]
    while frontier:
        current = frontier.pop(0)
        for _, target in successors(current):
            if any(same_node(target, known) for known in found):
                continue
            found.append(target)
            frontier.append(target)
    return tuple(found)


def routes(source: Node, target: Node) -> tuple[Route, ...]:
    """Every simple route from ``source`` to ``target`` in declaration order, depth-first."""
    if same_node(source, target):
        return ((),)
    found: list[Route] = []
    for step, next_node in successors(source):
        for suffix in routes(next_node, target):
            found.append((step, *suffix))
    return tuple(found)


def _assert_acyclic(start: Node, stack: tuple[Node, ...]) -> None:
    assert not any(same_node(start, seen) for seen in stack), (
        f"the selected structural graph has a cycle through {start.category!r}"
    )
    for _, target in successors(start):
        _assert_acyclic(target, (*stack, start))


def _local_methods(local_class: type) -> dict[str, Callable[..., Any]]:
    return {
        name: function
        for name, function in vars(local_class).items()
        if inspect.isfunction(function) and name not in _IGNORED_NAMES and (not name.startswith("_") or name.startswith("__"))
    }


def _is_subcategory(specific: Category, general: Category, role: Role) -> bool:
    return any(same_node(found, node(general, role)) for found in reachable(node(specific, role)))


def _merge(existing: Entry, candidate: Entry) -> Entry:
    if existing.owner is candidate.owner:
        return existing
    if _is_subcategory(existing.owner, candidate.owner, existing.role):
        return existing
    if _is_subcategory(candidate.owner, existing.owner, candidate.role):
        return candidate
    raise SemanticCollisionError(
        f"{existing.name!r} is declared by both {existing.owner!r} and {candidate.owner!r}, "
        "which are incomparable; name the two mathematical operations distinctly"
    )


def catalogue(current: Node) -> dict[str, Entry]:
    """The compiled method catalogue of one node, cached on its category."""
    catalogues = current.category.catalogues()
    if current.role in catalogues:
        return catalogues[current.role]
    local_class = current.category.local_role_class(current.role)
    entries = {
        name: Entry(current.category, current.role, name, function, ())
        for name, function in _local_methods(local_class).items()
    }
    for step, target in successors(current):
        for name, inherited in catalogue(target).items():
            if name in entries and not entries[name].route:
                continue
            candidate = inherited._replace(route=(step, *inherited.route))
            entries[name] = _merge(entries[name], candidate) if name in entries else candidate
    catalogues[current.role] = entries
    return entries


def empty_local_role(category: Category, role: Role) -> type[CategoryPoint]:
    """A local role class that declares nothing, on the kernel base of the ambient's role."""
    ambient_node = node(category.ambient(), role)
    ambient_class = ambient_node.category.role_class(ambient_node.role)
    kernel_bases = (kernel_base(Role.OBJECT), kernel_base(Role.ELEMENT), kernel_base(Role.MORPHISM), CategoryPoint)
    base = next(klass for klass in ambient_class.__mro__ if klass in kernel_bases)
    return type(f"{category!r}.{role.value}", (base,), {})


def compile_category(category: Category) -> None:
    """Compile the three role classes of ``category`` from its declarations."""
    functors = tuple(category.structure_functors())
    for functor in functors:
        functor_category = category.category().morphism_category(1)
        assert functor in functor_category, f"{functor!r} is not an object of {functor_category!r}"
        assert functor.domain() is category, f"{functor!r} does not have domain {category!r}"
    assert all(first is not second for index, first in enumerate(functors) for second in functors[index + 1 :]), (
        f"{category!r} selects one functor twice"
    )
    category.select_functors(functors)
    for role in Role:
        _assert_acyclic(node(category, role), ())
    for role in Role:
        current = node(category, role)
        if current.category is not category:
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        surface = {
            name: descriptors.forwarding_descriptor(entry)
            for name, entry in catalogue(current).items()
            if entry.route
        }
        if not functors and not surface:
            # Nothing is inherited: the local declaration is the role class itself, so
            # ``Cat().ObjectType is Category`` and ``Sets().ObjectType is SetObject``.
            setattr(category, role.value, category.local_role_class(role))
            continue
        codomain_classes: list[type] = []
        for _, target in successors(current):
            klass = target.category.role_class(target.role)
            if not any(klass is known for known in codomain_classes):
                codomain_classes.append(klass)
        # A codomain role class that another codomain role class already refines is in
        # that class's linearization; listing it too would precede its own subclass.
        bases = [category.local_role_class(role)] + [
            klass
            for klass in codomain_classes
            if not any(other is not klass and issubclass(other, klass) for other in codomain_classes)
        ]
        compiled = dynamic_class(
            f"{category!r}.{role.value}",
            tuple(bases),
            cls=type("Surface", (), surface),
            prepend_cls_bases=False,
        )
        setattr(category, role.value, compiled)
