"""The method compiler: catalogues, routes, and dynamic role classes (POL-CAT-016, POL-CAT-012, POL-KERNEL-001).

The selected graph is ``structure_functors()`` alone.  Its nodes are pairs
``(category, role)``; the node ``(Mor(C), object)`` *is* the node ``(C, morphism)``
(POL-CAT-021: one implementation type, one value, two placements), which
``Category.role_source`` normalizes.  A route is a simple directed path of steps
``(functor, role at the step's source)``; the graph reachable from a category is a
finite DAG, asserted at compile time (POL-CAT-012).

Method catalogue of a node (``specs/resolution.md``):

1. a local declaration takes precedence;
2. one declaring owner reached by several routes supplies one entry whose execution
   route is the first route in declaration order;
3. comparable owners yield the most specific one;
4. incomparable owners with one spelling raise ``SemanticCollisionError``.

The compiled role class is a Sage dynamic class (``sage.structure.dynamic_class``):
bases are the local role class followed by the codomain role classes of the
selected functors, and the surface holds one forwarding descriptor per inherited
name.  Method compilation constructs no value image (POL-KERNEL-001).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Concatenate, NamedTuple

from sage.structure.dynamic_class import dynamic_class

import sage_categories.kernel.descriptors as descriptors
from sage_categories.kernel.caches import MonoDict
from sage_categories.kernel.roles import CategoryPoint, Role, kernel_base

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "DeclaredMethod",
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

# A declaring method: its receiver is a value of the declaring role class, and its
# remaining parameters and result are exactly those of its typed signature
# (POL-CAT-075, POL-TYPE-028).
type DeclaredMethod[**P, R] = Callable[Concatenate[CategoryPoint, P], R]


class Entry[**P, R](NamedTuple):
    """One compiled method: its declaring owner and role, its spelling, its declaration, and its execution route."""

    owner: Category
    role: Role
    name: str
    function: DeclaredMethod[P, R]
    route: Route


_IGNORED_NAMES = frozenset({"__init__", "__new__", "__repr__", "__init_subclass__", "__class_getitem__"})

# The position of each role class in the global linearization order: the ordinal of
# the first category compiled with it (a local class with no inherited surface is the
# role class of every category that declares it, such as the identity 2-cells of
# every 1-category).
_class_keys: dict[type[CategoryPoint], int] = {}

# The local role class of each category that declares none of its own, keyed by
# identity: one declaring owner per node (POL-CAT-016).
_empty_local_roles: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


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


def _local_methods[**P, R](local_class: type[CategoryPoint]) -> dict[str, DeclaredMethod[P, R]]:
    """The methods declared on the class body of a local role class; the catalogue is heterogeneous in ``P`` and ``R``."""
    return {
        name: function
        for name, function in vars(local_class).items()
        if inspect.isfunction(function) and name not in _IGNORED_NAMES and (not name.startswith("_") or name.startswith("__"))
    }


def _is_subcategory(specific: Category, general: Category, role: Role) -> bool:
    return any(same_node(found, node(general, role)) for found in reachable(node(specific, role)))


def _merge[**P, R](existing: Entry[P, R], candidate: Entry[P, R]) -> Entry[P, R]:
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


def catalogue[**P, R](current: Node) -> dict[str, Entry[P, R]]:
    """The compiled method catalogue of one node, cached on its category; heterogeneous in ``P`` and ``R``."""
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
    """The local role class that declares nothing, on the kernel base of the ambient's role.

    One class per category and role, retained: the compiled bases of a category list
    the local class of every reachable node, and ``descriptors._declared`` finds a
    declaring owner by class identity.  A second class with the same name would be a
    second declaring owner of one node, and two of them in one base list have no
    consistent linearization (POL-CAT-016, POL-CAT-011).
    """
    table = _empty_local_roles[role]
    if category not in table:
        ambient_node = node(category.ambient(), role)
        ambient_class = ambient_node.category.role_class(ambient_node.role)
        kernel_bases = (kernel_base(Role.OBJECT), kernel_base(Role.ELEMENT), kernel_base(Role.MORPHISM), CategoryPoint)
        base = next(klass for klass in ambient_class.__mro__ if klass in kernel_bases)
        table[category] = type(f"{category!r}.{role.value}", (base,), {})
    return table[category]


def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile the three role classes of ``category`` from its local declarations and its selected functors."""
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
        # The bases are the role classes of every reachable node, in one global order:
        # the class compiled most recently first.  A selected functor's codomain is
        # compiled before its source, so this is a linear extension of the selected
        # graph; listing the whole closure in that order makes every compiled
        # linearization a subsequence of one total order, so the C3 merge never
        # conflicts (Sage's category framework fixes its linearizations the same way,
        # through ``_cmp_key`` and ``sage.misc.c3_controlled``).
        bases: list[type[CategoryPoint]] = [category.local_role_class(role)]
        for klass in sorted({found.category.role_class(found.role) for found in reachable(current)[1:]}, key=_class_keys.__getitem__, reverse=True):
            bases.append(klass)
        compiled = dynamic_class(
            f"{category!r}.{role.value}",
            tuple(bases),
            cls=type("Surface", (), surface),
            prepend_cls_bases=False,
        )
        setattr(category, role.value, compiled)
    for role in Role:
        _class_keys.setdefault(category.role_class(role), category.ordinal())
