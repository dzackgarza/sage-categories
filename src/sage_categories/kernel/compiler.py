"""The method compiler: catalogues, routes, and dynamic role classes (POL-CAT-016, POL-CAT-012, POL-KERNEL-001).

The selected graph is ``structure_functors()`` alone.  Its nodes are pairs
``(category, role)``; the node ``(Mor(C), object)`` *is* the node ``(C, morphism)``
(POL-CAT-021: one implementation type, one value, two placements), which
``Category.role_source`` normalizes.  A route is a simple directed path of steps
``(functor, role at the step's source)``; the graph reachable from a category is a
finite DAG, asserted at compile time (POL-CAT-012).

Method catalogue of a node (``specs/resolution.md``):

1. a local declaration takes precedence;
2. one declaring owner reached by several routes supplies one entry;
3. comparable owners yield the most specific one;
4. incomparable owners with one spelling raise ``SemanticCollisionError``.

The compiled role class is a Sage dynamic class (``sage.structure.dynamic_class``).
Its bases are exactly the *controlled* direct bases that
``sage.misc.c3_controlled.C3_sorted_merge`` returns for the node: compiled classes of
reachable nodes.  A node that reaches none ends its chain on its kernel role class.

A declaration is never a base.  It is passed as ``cls``, so its methods are inserted
into the compiled class and its own Python bases are dropped.  This is Sage's
``Category._make_named_class``, which passes ``ParentMethods`` the same way and warns
when a method provider has a super class at all.

That is what lets Python linearize the result.  ``C3_sorted_merge`` orders *nodes*;
every class it never sees is unconstrained, and Python then places it wherever each
individual class construction allows.  Two constructions rank one such pair opposite
ways, and a node reaching both has no MRO at all.  With declarations out of the bases,
every class in every compiled MRO is a node class or its role's kernel chain end, and
carries the node order; ``_assert_linearized`` holds that.

Each compiled node owns one generated constructor wrapper.  Before that wrapper starts
the local ``super()`` chain, every selected functor converts the complete source input
to the retained input of its canonical target.  The wrappers then consume those inputs
in C3 order and initialize every reachable node once (POL-KERNEL-028/029).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import CellType, FunctionType, GenericAlias
from typing import TYPE_CHECKING, Concatenate, NamedTuple

from sage.misc.c3_controlled import C3_sorted_merge
from sage.structure.dynamic_class import dynamic_class

from sage_categories.kernel.caches import MonoDict, retain_constructed_transport
from sage_categories.kernel.construction import (
    ArrowStageIdentity,
    ElementConstructionContext,
    ElementConstructionInput,
    ElementRoleIdentity,
    GeneralCategoryPointIdentity,
    MorphismConstructionContext,
    MorphismConstructionInput,
    MorphismRoleIdentity,
    ObjectConstructionContext,
    ObjectConstructionInput,
    ObjectRoleIdentity,
    ObjectStageIdentity,
    activate_element_context,
    activate_morphism_context,
    activate_object_context,
    active_construction_context,
    deactivate_element_context,
    deactivate_morphism_context,
    deactivate_object_context,
    retain_element_input,
    retain_morphism_input,
    retain_object_input,
)
from sage_categories.kernel.roles import (
    CategoryPoint,
    CategoryPointKernel,
    MorphismOfCategory,
    ObjectOfCategory,
    Role,
    cat_element_root,
    kernel_base,
)

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
    """One compiled method: its declaring owner and role, spelling, and declaration."""

    owner: Category
    role: Role
    name: str
    function: DeclaredMethod[P, R]


_IGNORED_NAMES = frozenset({"__init__", "__new__", "__repr__", "__init_subclass__", "__class_getitem__"})

# The local role class of each category that declares none of its own, keyed by
# identity: one declaring owner per node (POL-CAT-016).
_empty_local_roles: dict[Role, MonoDict] = {role: MonoDict() for role in Role}

# Per role: the C3 linearization of each node and the controlled direct bases its
# class is built from, keyed by the node's category; and the node of each node key.
_linearizations: dict[Role, MonoDict] = {role: MonoDict() for role in Role}
_nodes_by_key: dict[int, Node] = {}

_ROLE_POSITIONS: dict[Role, int] = {
    Role.ELEMENT: 0,
    Role.MORPHISM: 1,
    Role.OBJECT: 2,
}

_COMPILE_ORDER = (Role.ELEMENT, Role.OBJECT, Role.MORPHISM)


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


def _is_cat_element_root(current: Node) -> bool:
    """Whether ``current`` is the preallocated common ``Cat().ElementType`` node."""
    return current.role is Role.ELEMENT and current.category.category() is current.category


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


def _reaches_owner(specific: Entry, general: Entry) -> bool:
    """Whether the declaring node of ``specific`` reaches that of ``general``."""
    specific_node = node(specific.owner, specific.role)
    general_node = node(general.owner, general.role)
    if same_node(specific_node, general_node):
        return True
    if _is_cat_element_root(general_node):
        return True
    if specific_node.role is not general_node.role:
        return False
    return any(same_node(found, general_node) for found in reachable(specific_node))


def _merge[**P, R](existing: Entry[P, R], candidate: Entry[P, R]) -> Entry[P, R]:
    if existing.owner is candidate.owner and existing.role is candidate.role:
        return existing
    if _reaches_owner(existing, candidate):
        return existing
    if _reaches_owner(candidate, existing):
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
        name: Entry(current.category, current.role, name, function)
        for name, function in _local_methods(local_class).items()
    }
    for _, target in successors(current):
        for name, inherited in catalogue(target).items():
            if name in entries and entries[name].owner is current.category:
                continue
            entries[name] = _merge(entries[name], inherited) if name in entries else inherited
    if not _is_cat_element_root(current):
        cat_element = node(current.category.category(), Role.ELEMENT)
        for name, inherited in catalogue(cat_element).items():
            if name in entries and entries[name].owner is current.category and entries[name].role is current.role:
                continue
            entries[name] = _merge(entries[name], inherited) if name in entries else inherited
    catalogues[current.role] = entries
    return entries


def empty_local_role(category: Category, role: Role) -> type[CategoryPoint]:
    """The local role declaration that introduces no members or state.

    One class per category and role, retained: it names the declaring owner of the node
    and stands directly on the role's kernel base (POL-CAT-053, POL-KERNEL-028).
    """
    table = _empty_local_roles[role]
    if category not in table:
        table[category] = type(f"Declared{category!r}.{role.value}", (kernel_base(role),), {})
    return table[category]


def _selected_targets(current: Node) -> tuple[Node, ...]:
    """The distinct nodes one selected step from ``current``, most recently constructed first.

    The C3 merge takes the direct supers in the order of the total order, not in
    declaration order: Sage sorts them the same way (``Category._super_categories``
    applies ``Category._sort``, decreasing in ``_cmp_key``).  A category's ambient is
    declared first and constructed first, so declaration order is the wrong one here.
    Constructor route order still reads ``successors`` directly.
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


def _base_classes(current: Node) -> tuple[type[CategoryPoint], ...]:
    """The controlled direct bases of ``current``'s class: compiled role classes only.

    The controlled list is passed through as it is.  Its entries are not only the
    direct targets: C3 adds the control edges that make the merge succeed, and
    dropping one because another base already derives from it discards exactly the
    guarantee the algorithm provides.  Sage passes ``_super_categories_for_classes``
    to its class construction unchanged for the same reason.

    One adjustment is forced by Python rather than by the algorithm.  Several nodes can
    share one compiled class — the node ``(Mor(C), object)`` *is* the node
    ``(C, morphism)``, and its class is installed on both categories.  A base list may
    not repeat a class, and the shared class belongs at the *last* of its positions: it
    is an ancestor of whatever the higher-ranked nodes contribute, so keeping an earlier
    occurrence would place it above its own descendants.  Nothing is dropped, so every
    control edge survives.

    A node that reaches no other node ends on its role's kernel class.  A declaration is
    never a base: its members are copied into its one compiled node.
    """
    if _is_cat_element_root(current):
        return (CategoryPointKernel,)
    keys = _linearize(current)[1]
    classes = [_nodes_by_key[key].category.role_class(_nodes_by_key[key].role) for key in keys]
    bases = [klass for position, klass in enumerate(classes) if not any(later is klass for later in classes[position + 1 :])]
    if not bases:
        bases = [kernel_base(current.role)]
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


def _rebound(function: FunctionType, cell: CellType) -> FunctionType:
    """A copy of ``function`` whose ``__class__`` closure cell is ``cell``.

    A method declared with zero-argument ``super()`` closes over ``__class__``, bound by
    Python to the class whose body defined it.  That class is the declaration, which is
    not in the compiled MRO, so the original closure would make ``super()`` reject its
    own receiver.  Rebinding the cell to the compiled class makes ``super()`` enter the
    compiled chain, which is the chain the call is about.  The function is copied rather
    than mutated: one declaration can be compiled at several nodes.
    """
    position = function.__code__.co_freevars.index("__class__")
    assert function.__closure__ is not None, function
    closure = tuple(cell if index == position else held for index, held in enumerate(function.__closure__))
    copy = FunctionType(function.__code__, function.__globals__, function.__name__, function.__defaults__, closure)
    copy.__qualname__ = function.__qualname__
    copy.__kwdefaults__ = function.__kwdefaults__
    copy.__annotations__ = function.__annotations__
    return copy


_CLASS_METADATA = frozenset({"__dict__", "__weakref__", "__qualname__", "__classcell__"})


def _rebound_member(value, cell: CellType):
    uses_super = isinstance(value, FunctionType) and "__class__" in value.__code__.co_freevars
    return _rebound(value, cell) if uses_super else value


def _local_initializer(local: type[CategoryPoint], cell: CellType) -> FunctionType | None:
    """The declaration's initializer, rebound to its compiled node and kept out of the copied members."""
    initializer = vars(local).get("__init__")
    if not isinstance(initializer, FunctionType):
        return None
    return _rebound_member(initializer, cell)


def _method_provider(
    local: type[CategoryPoint],
    cell: CellType,
    initializer: FunctionType,
) -> type:
    """A Sage method provider containing local members and the generated wrapper."""
    provider = type(local.__name__, (), {})
    for name, value in vars(local).items():
        if name in _CLASS_METADATA or name == "__init__":
            continue
        setattr(provider, name, _rebound_member(value, cell))
    # PEP 695 adds ``typing.Generic`` below a parameterized declaration.  That raw
    # base cannot enter the public role MRO (POL-KERNEL-028).  Preserve subscription
    # with Python's standard generic-alias constructor instead.  The declaration's
    # ``__type_params__`` and ``__parameters__`` were copied above.
    if vars(local).get("__type_params__", ()) and "__class_getitem__" not in vars(local):
        provider.__class_getitem__ = classmethod(GenericAlias)
    setattr(provider, "__init__", initializer)
    return provider


def _assert_linearized(current: Node, compiled: type[CategoryPoint]) -> None:
    """The MRO is the node linearization followed by exactly one kernel role chain.

    Sage states the same invariant in ``Category._test_category_graph``
    (``sage/categories/category.py``): ``parent_class.mro()`` is the ancestors'
    compiled classes followed by the common Python chain end.  Raw declarations never
    occur in this order (POL-KERNEL-028).
    """
    if _is_cat_element_root(current):
        expected = (compiled, *CategoryPointKernel.__mro__)
        actual = tuple(compiled.__mro__)
        assert actual == expected, (
            f"the Cat.ElementType MRO is {[klass.__name__ for klass in actual]}, expected "
            f"{[klass.__name__ for klass in expected]}"
        )
        return
    order = [_nodes_by_key[key] for key in _linearize(current)[0]]
    classes = [found.category.role_class(found.role) for found in order]
    expected = (compiled, *classes, *kernel_base(current.role).__mro__)
    actual = tuple(compiled.__mro__)
    assert actual == expected, (
        f"the {current.role.value} MRO of {current.category!r} is "
        f"{[klass.__name__ for klass in actual]}, expected "
        f"{[klass.__name__ for klass in expected]}"
    )


def _route_name(route: Route) -> str:
    return " then ".join(repr(functor) for functor, _ in route) or "the identity route"


class _NodeRuntime(NamedTuple):
    initializer: FunctionType | None
    cell: CellType


_node_runtimes: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


def _runtime(current: Node) -> _NodeRuntime:
    table = _node_runtimes[current.role]
    assert current.category in table, f"the {current.role.value} runtime of {current.category!r} is not compiled"
    return table[current.category]


def _advance(cell: CellType, instance: CategoryPoint) -> None:
    """Enter the next generated wrapper, or the kernel role initializer."""
    super(cell.cell_contents, instance).__init__()


def _object_step[Value: ObjectOfCategory, Datum](
    current: Node,
    construction_input: ObjectConstructionInput[Value, Datum],
    instance: ObjectOfCategory,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        if runtime.initializer is None:
            _advance(runtime.cell, instance)
            return
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _element_step[Value: CategoryPoint, Datum](
    current: Node,
    construction_input: ElementConstructionInput[Value, Datum],
    instance: Value,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        if runtime.initializer is None:
            _advance(runtime.cell, instance)
            return
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _morphism_step[Value: MorphismOfCategory, Datum](
    current: Node,
    construction_input: MorphismConstructionInput[Value, Datum],
    instance: MorphismOfCategory,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        if runtime.initializer is None:
            _advance(runtime.cell, instance)
            return
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _object_steps[RootValue: ObjectOfCategory, RootDatum](
    current: Node,
    root: ObjectConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact object input into one zero-argument C3 node step."""
    assert current.role is Role.OBJECT
    found: list[tuple[Node, int, ObjectOfCategory, Callable[[], None], Route]] = []

    def visit[Value: ObjectOfCategory, Datum](
        source: Node,
        source_input: ObjectConstructionInput[Value, Datum],
        route: Route,
    ) -> None:
        known = next(((identity, image, first_route) for owner, identity, image, _, first_route in found if same_node(owner, source)), None)
        if known is None:
            retain_constructed_transport(root, source.category, source_input)
            found.append((source, id(source_input), source_input.canonical_image, _object_step(source, source_input, root.canonical_image), route))
        else:
            identity, image, first_route = known
            if identity != id(source_input) or image is not source_input.canonical_image:
                raise StructuralImageMismatch(
                    f"the object routes {_route_name(first_route)} and {_route_name(route)} to "
                    f"{source.category!r} return distinct canonical images or construction inputs"
                )
        for step, target in successors(source):
            functor, _ = step
            target_input = functor.object_constructor_input(source_input)
            assert isinstance(target_input, ObjectConstructionInput), f"{functor!r} returned no object construction input"
            visit(target, target_input, (*route, step))

    visit(current, root, ())
    expected = reachable(current)
    assert all(any(same_node(owner, target) for owner, _, _, _, _ in found) for target in expected)
    return tuple((target, next(step for owner, _, _, step, _ in found if same_node(owner, target))) for target in expected)


def _element_steps[RootValue: ElementOfObject, RootDatum](
    current: Node,
    root: ElementConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact element input into one zero-argument C3 node step."""
    assert current.role is Role.ELEMENT
    found: list[tuple[Node, int, CategoryPoint, Callable[[], None], Route]] = []

    def visit[Value: ElementOfObject, Datum](
        source: Node,
        source_input: ElementConstructionInput[Value, Datum],
        route: Route,
    ) -> None:
        known = next(((identity, image, first_route) for owner, identity, image, _, first_route in found if same_node(owner, source)), None)
        if known is None:
            retain_constructed_transport(root, source.category, source_input)
            found.append((source, id(source_input), source_input.canonical_image, _element_step(source, source_input, root.canonical_image), route))
        else:
            identity, image, first_route = known
            if identity != id(source_input) or image is not source_input.canonical_image:
                raise StructuralImageMismatch(
                    f"the element routes {_route_name(first_route)} and {_route_name(route)} to "
                    f"{source.category!r} return distinct canonical images or construction inputs"
                )
        for step, target in successors(source):
            functor, _ = step
            target_input = functor.element_constructor_input(source_input)
            assert isinstance(target_input, ElementConstructionInput), f"{functor!r} returned no element construction input"
            visit(target, target_input, (*route, step))

    visit(current, root, ())
    expected = reachable(current)
    assert all(any(same_node(owner, target) for owner, _, _, _, _ in found) for target in expected)
    return tuple((target, next(step for owner, _, _, step, _ in found if same_node(owner, target))) for target in expected)


def _object_cat_element_step[Value: ObjectOfCategory, Datum](
    root: ObjectConstructionInput[Value, Datum],
) -> tuple[Node, Callable[[], None]]:
    """The stage-``1`` input at the common ``Cat().ElementType`` MRO root."""
    target = node(root.identity.category.category(), Role.ELEMENT)
    stage_input = ElementConstructionInput(root.canonical_image, ObjectStageIdentity(root.identity.category), None)
    return target, _element_step(target, stage_input, root.canonical_image)


def _element_cat_element_step[Value: ElementOfObject, Datum](
    root: ElementConstructionInput[Value, Datum],
) -> tuple[Node, Callable[[], None]]:
    """The defining-morphism input at the common ``Cat().ElementType`` MRO root."""
    assert isinstance(root.identity, GeneralCategoryPointIdentity)
    target = node(root.identity.defining_morphism.base_category().category(), Role.ELEMENT)
    stage_input = ElementConstructionInput(root.canonical_image, root.identity, None)
    return target, _element_step(target, stage_input, root.canonical_image)


def _morphism_cat_element_step[Value: MorphismOfCategory, Datum](
    root: MorphismConstructionInput[Value, Datum],
) -> tuple[Node, Callable[[], None]]:
    """The stage-``[1]`` input at the common ``Cat().ElementType`` MRO root."""
    parent = root.identity.category.base_category()
    target = node(parent.category(), Role.ELEMENT)
    identity = ArrowStageIdentity(parent, root.identity.domain, root.identity.codomain)
    stage_input = ElementConstructionInput(root.canonical_image, identity, None)
    return target, _element_step(target, stage_input, root.canonical_image)


def _morphism_steps[RootValue: MorphismOfCategory, RootDatum](
    current: Node,
    root: MorphismConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact morphism input into one zero-argument C3 node step."""
    assert current.role is Role.MORPHISM
    found: list[tuple[Node, int, MorphismOfCategory, Callable[[], None], Route]] = []

    def visit[Value: MorphismOfCategory, Datum](
        source: Node,
        source_input: MorphismConstructionInput[Value, Datum],
        route: Route,
    ) -> None:
        known = next(((identity, image, first_route) for owner, identity, image, _, first_route in found if same_node(owner, source)), None)
        if known is None:
            retain_constructed_transport(root, source.category, source_input)
            found.append((source, id(source_input), source_input.canonical_image, _morphism_step(source, source_input, root.canonical_image), route))
        else:
            identity, image, first_route = known
            if identity != id(source_input) or image is not source_input.canonical_image:
                raise StructuralImageMismatch(
                    f"the morphism routes {_route_name(first_route)} and {_route_name(route)} to "
                    f"{source.category!r} return distinct canonical images or construction inputs"
                )
        for step, target in successors(source):
            functor, _ = step
            target_input = functor.morphism_constructor_input(source_input)
            assert isinstance(target_input, MorphismConstructionInput), f"{functor!r} returned no morphism construction input"
            visit(target, target_input, (*route, step))

    visit(current, root, ())
    expected = reachable(current)
    assert all(any(same_node(owner, target) for owner, _, _, _, _ in found) for target in expected)
    return tuple((target, next(step for owner, _, _, step, _ in found if same_node(owner, target))) for target in expected)


def _construct_object_root[Datum](
    current: Node,
    instance: ObjectOfCategory,
    identity: ObjectRoleIdentity,
    data: Datum,
) -> None:
    root = ObjectConstructionInput(instance, identity, data)
    retain_object_input(root)
    cat_element_identity = ObjectStageIdentity(identity.category)
    steps = (*_object_steps(current, root), _object_cat_element_step(root))
    context = ObjectConstructionContext(root.canonical_image, root.identity, cat_element_identity, steps)
    token = activate_object_context(context)
    try:
        context.run(current)
        context.assert_complete()
    finally:
        deactivate_object_context(token)


def _construct_element_root[Datum](
    current: Node,
    instance: CategoryPoint,
    identity: ElementRoleIdentity,
    data: Datum,
) -> None:
    root = ElementConstructionInput(instance, identity, data)
    retain_element_input(root)
    steps = _element_steps(current, root)
    cat_element_step = _element_cat_element_step(root)
    if not any(same_node(owner, cat_element_step[0]) for owner, _ in steps):
        steps = (*steps, cat_element_step)
    context = ElementConstructionContext(root.canonical_image, root.identity, root.identity, steps)
    token = activate_element_context(context)
    try:
        context.run(current)
        context.assert_complete()
    finally:
        deactivate_element_context(token)


def _construct_morphism_root[Datum](
    current: Node,
    instance: MorphismOfCategory,
    identity: MorphismRoleIdentity,
    data: Datum,
) -> None:
    root = MorphismConstructionInput(instance, identity, data)
    retain_morphism_input(root)
    parent = identity.category.base_category()
    cat_element_identity = ArrowStageIdentity(parent, identity.domain, identity.codomain)
    steps = (*_morphism_steps(current, root), _morphism_cat_element_step(root))
    context = MorphismConstructionContext(root.canonical_image, root.identity, cat_element_identity, steps)
    token = activate_morphism_context(context)
    try:
        context.run(current)
        context.assert_complete()
    finally:
        deactivate_morphism_context(token)


def initialize_category_declaration(instance: ObjectOfCategory, universe: Category) -> None:
    """Initialize a category class defined before ``Category`` names ``Cat().ObjectType``.

    Its Python base is the provisional local declaration, so the call is already inside
    that node initializer.  This finite bootstrap path initializes the two remaining
    classes in the exact public tail: ``ObjectOfCategory`` and ``Cat().ElementType``.
    """
    identity = ObjectRoleIdentity(universe)
    root = ObjectConstructionInput(instance, identity, None)
    retain_object_input(root)
    cat_element_identity = ObjectStageIdentity(universe)
    context = ObjectConstructionContext(
        root.canonical_image,
        root.identity,
        cat_element_identity,
        (_object_cat_element_step(root),),
    )
    token = activate_object_context(context)
    try:
        ObjectOfCategory.__init__(instance, universe)
        context.assert_complete()
    finally:
        deactivate_object_context(token)


def _object_wrapper(current: Node) -> FunctionType:

    def initialize[Datum](
        instance: ObjectOfCategory,
        category: Category | None = None,
        data: Datum | None = None,
    ) -> None:
        active = active_construction_context(instance)
        if active is not None and active.canonical_image is instance:
            assert category is None and data is None, "an ancestor object constructor receives only its precomputed input"
            active.run(current)
            return
        if category is None:
            category = current.category
        assert category is current.category, f"the {current.category!r} object role cannot construct an object of {category!r}"
        identity = ObjectRoleIdentity(category)
        if data is None:
            _construct_object_root(current, instance, identity, None)
            return
        _construct_object_root(current, instance, identity, data)

    initialize.__name__ = "__init__"
    return initialize


def _element_wrapper(current: Node) -> FunctionType:

    def initialize[Datum](
        instance: CategoryPoint,
        defining_morphism: MorphismOfCategory | None = None,
        data: Datum | None = None,
    ) -> None:
        active = active_construction_context(instance)
        if active is not None and active.canonical_image is instance:
            assert defining_morphism is None and data is None, "an ancestor element constructor receives only its precomputed input"
            active.run(current)
            return
        assert defining_morphism is not None, "an element root constructor requires its defining morphism"
        identity = ElementRoleIdentity(defining_morphism)
        if data is None:
            _construct_element_root(current, instance, identity, None)
            return
        _construct_element_root(current, instance, identity, data)

    initialize.__name__ = "__init__"
    return initialize


def _morphism_wrapper(current: Node) -> FunctionType:

    def initialize[Datum](
        instance: MorphismOfCategory,
        category: Category | None = None,
        domain: ObjectOfCategory | None = None,
        codomain: ObjectOfCategory | None = None,
        data: Datum | None = None,
    ) -> None:
        active = active_construction_context(instance)
        if active is not None and active.canonical_image is instance:
            assert category is None and domain is None and codomain is None and data is None, (
                "an ancestor morphism constructor receives only its precomputed input"
            )
            active.run(current)
            return
        assert category is not None and domain is not None and codomain is not None, (
            "a morphism root constructor requires its category and endpoints"
        )
        identity = MorphismRoleIdentity(category, domain, codomain)
        if data is None:
            _construct_morphism_root(current, instance, identity, None)
            return
        _construct_morphism_root(current, instance, identity, data)

    initialize.__name__ = "__init__"
    return initialize


def _constructor_wrapper(current: Node) -> FunctionType:
    match current.role:
        case Role.OBJECT:
            return _object_wrapper(current)
        case Role.ELEMENT:
            return _element_wrapper(current)
        case Role.MORPHISM:
            return _morphism_wrapper(current)
    raise AssertionError(current.role)


def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile the three role classes of ``category`` from its local declarations and its selected functors."""
    for functor in functors:
        functor_category = category.category().morphism_category(1)
        assert functor in functor_category, f"{functor!r} is not an object of {functor_category!r}"
        assert functor.domain() is category, f"{functor!r} does not have domain {category!r}"
        functor._assert_complete_constructor_conversions()
    assert all(first is not second for index, first in enumerate(functors) for second in functors[index + 1 :]), (
        f"{category!r} selects one functor twice"
    )
    category.select_functors(functors)
    for role in _COMPILE_ORDER:
        _assert_acyclic(node(category, role), ())
    for role in _COMPILE_ORDER:
        current = node(category, role)
        _linearize(current)
        if current.category is not category:
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        # Catalogue construction rejects semantic collisions.  Inherited execution
        # itself is ordinary Python lookup through the controlled compiled MRO.
        catalogue(current)
        # Every node gets its own compiled class, including one that declares nothing
        # and inherits nothing: in Sage a category without ``ParentMethods`` still has
        # its own ``parent_class``, built from its super categories and adding no
        # methods.  The declaration supplies methods through ``cls`` and never becomes a
        # base, so every class in the compiled MRO is a node class and carries the node
        # order (POL-CAT-016).
        #
        # The declared class stays what it was: ``local_role_class`` reads the class
        # attribute, ``role_class`` the compiled instance attribute.
        local = category.local_role_class(role)
        bases = _base_classes(current)
        cell = CellType()
        node_initializer = _local_initializer(local, cell)
        wrapper = _constructor_wrapper(current)
        provider = _method_provider(local, cell, wrapper)
        if _is_cat_element_root(current):
            compiled = cat_element_root()
            assert compiled.__bases__ == bases
            for name, value in vars(provider).items():
                if name not in _CLASS_METADATA:
                    setattr(compiled, name, value)
            compiled.__doc__ = local.__doc__
        else:
            try:
                compiled = dynamic_class(
                    f"{category!r}.{role.value}",
                    bases,
                    cls=provider,
                    doccls=local,
                    prepend_cls_bases=False,
                )
            except TypeError as conflict:
                raise TypeError(
                    f"the {role.value} class of {category!r} has no linearization over "
                    f"{[klass.__name__ for klass in bases]}: {conflict}"
                ) from conflict
        cell.cell_contents = compiled
        _node_runtimes[role][category] = _NodeRuntime(node_initializer, cell)
        setattr(category, role.value, compiled)
        _assert_linearized(current, compiled)
