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
its bases are the local role class followed by the *controlled* direct bases that
``sage.misc.c3_controlled.C3_sorted_merge`` returns for the node, and the surface
holds one forwarding descriptor per inherited name.  Sage's algorithm builds the
local information from the bare hierarchy so that Python's C3 never fails; hand-kept
base orders do fail on a hierarchy this shape, which is the problem that module was
written for.  Method compilation constructs no value image (POL-KERNEL-001).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Concatenate, NamedTuple

from sage.misc.c3_controlled import C3_sorted_merge
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

# The local role class of each category that declares none of its own, keyed by
# identity: one declaring owner per node (POL-CAT-016).
_empty_local_roles: dict[Role, MonoDict] = {role: MonoDict() for role in Role}

# Per role: the C3 linearization of each node and the controlled direct bases its
# class is built from, keyed by the node's category; and the node of each node key.
_linearizations: dict[Role, MonoDict] = {role: MonoDict() for role in Role}
_nodes_by_key: dict[int, Node] = {}

_ROLE_POSITIONS: dict[Role, int] = {role: position for position, role in enumerate(Role)}


def node_key(current: Node) -> int:
    """The position of ``current`` in the total order the C3 merge is controlled by.

    A category is constructed after every category it selects a functor into, so its
    ordinal already ranks it above them; the role breaks the tie between the object
    node and the morphism node of one category, which are distinct nodes that no
    selected functor relates.
    """
    return current.category.ordinal() * len(Role) + _ROLE_POSITIONS[current.role]


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


def _selected_targets(current: Node) -> tuple[Node, ...]:
    """The distinct nodes one selected step from ``current``, most recently constructed first.

    The C3 merge takes the direct supers in the order of the total order, not in
    declaration order: Sage sorts them the same way (``Category._super_categories``
    applies ``Category._sort``, decreasing in ``_cmp_key``).  A category's ambient is
    declared first and constructed first, so declaration order is the wrong one here.
    Route order and catalogue precedence still read ``successors`` directly.
    """
    found: list[Node] = []
    for _, target in successors(current):
        if not any(same_node(target, known) for known in found):
            found.append(target)
    return tuple(sorted(found, key=node_key, reverse=True))


def _name_of(key: int) -> str:
    found = _nodes_by_key.get(key)
    return f"{found.category!r}.{found.role.value}" if found else f"an uncompiled node (key {key})"


def _out_of_order(current: Node, merged: list[int]) -> str:
    """The first pair of the linearization that construction order ranks the wrong way."""
    below, above = next((first, second) for first, second in zip(merged, merged[1:]) if first < second)
    return (
        f"the {current.role.value} linearization of {current.category!r} "
        f"is not sorted by construction order: it places {_name_of(below)} above {_name_of(above)}.  "
        "A category must be constructed after every category it selects a functor into."
    )


def _linearize(current: Node) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """The nodes ``current`` inherits from in C3 order, and its controlled direct bases.

    Both are tuples of node keys.  The reference implementation is Sage's
    ``Category._all_super_categories`` (``sage/categories/category.py``): merge the
    linearizations of the direct supers together with the list of direct supers, then
    build the class from the *second* value ``C3_sorted_merge`` returns — the direct
    bases carrying whatever control edges C3 needed.  Doing that is what guarantees
    Python's C3 never fails on a large hierarchy (``sage.misc.c3_controlled``).

    Nodes are merged as the integers ``node_key`` gives them: they compare by value,
    they are already assigned when a node is reached, and every node ranks strictly
    above every node it reaches, which is the total order the algorithm requires
    (Sage states the same invariant for ``_cmp_key``).
    """
    table = _linearizations[current.role]
    if current.category not in table:
        _nodes_by_key[node_key(current)] = current
        targets = _selected_targets(current)
        merged: list[int] = []
        bases: list[int] = []
        if targets:
            merged, bases = C3_sorted_merge(
                [[node_key(target), *_linearize(target)[0]] for target in targets]
                + [[node_key(target) for target in targets]]
            )
            assert sorted(merged, reverse=True) == merged, _out_of_order(current, merged)
        table[current.category] = (tuple(merged), tuple(bases))
    return table[current.category]


def _base_classes(current: Node, local: type[CategoryPoint]) -> tuple[type[CategoryPoint], ...]:
    """The controlled direct bases of ``current``'s class, as role classes after ``local``.

    The controlled list is passed through as it is.  Its entries are not only the
    direct targets: C3 adds the control edges that make the merge succeed, and
    dropping one because another base already derives from it discards exactly the
    guarantee the algorithm provides.  Sage passes ``_super_categories_for_classes``
    to its class construction unchanged for the same reason.

    Two adjustments are forced by Python rather than by the algorithm.  Several nodes
    can share one role class — a category that declares nothing and inherits nothing
    keeps the class it declares, and several categories declare one class, such as the
    identity 2-cells of every 1-category.  A base list may not repeat a class, and the
    shared class belongs at the *last* of its positions: it is an ancestor of whatever
    the higher-ranked nodes contribute, so keeping an earlier occurrence would place it
    above its own descendants.  Nothing is dropped, so every control edge survives.

    The local class is prepended only when no controlled base already derives from it:
    a category that declares nothing at this role has the bare kernel base as its local
    class, and prepending that would invert the order the same way.
    """
    keys = _linearize(current)[1]
    classes = [_nodes_by_key[key].category.role_class(_nodes_by_key[key].role) for key in keys]
    bases = [klass for position, klass in enumerate(classes) if not any(later is klass for later in classes[position + 1 :])]
    if not any(issubclass(klass, local) for klass in bases):
        bases.insert(0, local)
    inverted = [
        (earlier, later)
        for position, earlier in enumerate(bases)
        for later in bases[position + 1 :]
        if issubclass(later, earlier)
    ]
    assert not inverted, (
        f"the {current.role.value} bases of {current.category!r} place {inverted[0][0].__name__} "
        f"before {inverted[0][1].__name__}, which derives from it"
    )
    return tuple(bases)


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
        _linearize(current)
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
        # The local declaration first, then the controlled direct bases Sage's C3
        # returns for this node (``_linearize``).
        compiled = dynamic_class(
            f"{category!r}.{role.value}",
            _base_classes(current, category.local_role_class(role)),
            cls=type("Surface", (), surface),
            prepend_cls_bases=False,
        )
        setattr(category, role.value, compiled)
