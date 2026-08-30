"""Compile local declarations and selected target classes for the current kernel."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import CellType, FunctionType
from typing import TYPE_CHECKING, Concatenate, Generic, NamedTuple

from sage.categories.category import Category as SageCategory
from sage.misc.c3_controlled import C3_sorted_merge
from sage.misc.lazy_attribute import lazy_attribute
from sage.structure.dynamic_class import dynamic_class

from sage_categories.kernel.caches import MonoDict, canonical_images, retain_constructed_transport
from sage_categories.kernel.construction import (
    CategoryPointIdentity,
    ElementConstructionContext,
    ElementConstructionInput,
    ElementRoleIdentity,
    MorphismConstructionContext,
    MorphismConstructionInput,
    MorphismRoleIdentity,
    ObjectConstructionContext,
    ObjectConstructionInput,
    ObjectRoleIdentity,
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
    retained_object_input,
)
from sage_categories.kernel.roles import (
    CategoryPoint,
    MorphismOfCategory,
    ObjectOfCategory,
    Role,
    install_cat_element_root,
    kernel_base,
)

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "DeclaredMethod",
    "Entry",
    "Node",
    "SemanticCollisionError",
    "building_role_class",
    "building_role_classes",
    "catalogue",
    "compile_category",
    "controlled_bases",
    "element_inputs",
    "install_level_shift",
    "install_on_declaration",
    "morphism_inputs",
    "node",
    "object_inputs",
    "reachable",
    "recompile_category",
    "same_node",
]


class SemanticCollisionError(Exception):
    """Two incomparable owners declare one method spelling (POL-CAT-011, POL-API-011)."""


class _KernelRoleRootCategory(SageCategory):
    """A private Sage category for the final implementation class of one role."""

    def __init__(self, role: Role) -> None:
        self._role = role
        self.ParentMethods = kernel_base(role)
        super().__init__()

    @property
    def _cmp_key(self) -> int:
        return _ROLE_POSITIONS[self._role] - len(Role)

    def super_categories(self) -> list[SageCategory]:
        return []


class _RuntimeImplementationCategory(SageCategory):
    """A private Sage category whose ``parent_class`` is one owned implementation role."""

    def __init__(self, current: Node, targets: tuple[SageCategory, ...]) -> None:
        self._current = current
        self._targets = targets
        self.ParentMethods = current.category.local_role_class(current.role)
        super().__init__()

    @property
    def _cmp_key(self) -> int:
        return node_key(self._current)

    def super_categories(self) -> list[SageCategory]:
        return list(self._targets)

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        return self._make_named_class("parent_class", "ParentMethods", cache=True)


class Node(NamedTuple):
    category: Category
    role: Role


_runtime_categories: dict[Role, MonoDict] = {role: MonoDict() for role in Role}
_kernel_role_roots: dict[Role, _KernelRoleRootCategory] = {}


def _kernel_role_root(role: Role) -> _KernelRoleRootCategory:
    """The identity-cached private Sage category for one kernel role root."""
    if role not in _kernel_role_roots:
        _kernel_role_roots[role] = _KernelRoleRootCategory(role)
    return _kernel_role_roots[role]


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

# Where a run of written declarations ends: the kernel's own chain, which every role class
# reaches and which no category writes.
_KERNEL_CLASSES = frozenset({*(kernel_base(role) for role in Role), CategoryPoint, object})

# Whether the kernel is building a role class right now.  A role class over a category
# class is a subclass of it, so it reaches that class's own ``__init_subclass__``; it
# states no category and declares no roles (POL-CAT-057).
_building_role_class = False


def building_role_class() -> bool:
    """Whether the class being created is one the kernel is building rather than one a module writes."""
    return _building_role_class


@contextmanager
def building_role_classes() -> Iterator[None]:
    """Mark the kernel's own class construction, so the declaration check skips what it builds."""
    global _building_role_class
    previous, _building_role_class = _building_role_class, True
    try:
        yield
    finally:
        _building_role_class = previous

# The construction input a node carries, by the role the node lives in.
_INPUT_TYPES: dict[Role, type] = {
    Role.OBJECT: ObjectConstructionInput,
    Role.ELEMENT: ElementConstructionInput,
    Role.MORPHISM: MorphismConstructionInput,
}


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


def _runtime_category(current: Node) -> _RuntimeImplementationCategory:
    """The identity-cached Sage category that owns ``current``'s compiled role class."""
    table = _runtime_categories[current.role]
    if current.category in table:
        return table[current.category]
    targets: tuple[SageCategory, ...] = tuple(_runtime_category(target) for _, target in successors(current))
    if not targets:
        targets = (_kernel_role_root(Role.ELEMENT if _is_cat_element_root(current) else current.role),)
    targets = tuple(sorted(targets, key=lambda target: target._cmp_key, reverse=True))
    runtime = _RuntimeImplementationCategory(current, targets)
    table[current.category] = runtime
    return runtime


def _is_cat_element_root(current: Node) -> bool:
    """Whether ``current`` is the preallocated common ``Cat().ElementType`` node."""
    return current.role is Role.ELEMENT and current.category.category() is current.category


def successors(current: Node) -> tuple[tuple[Functor, Node], ...]:
    """The selected functors out of ``current``; each keeps the role it starts in."""
    return tuple(
        (functor, node(functor.codomain(), current.role))
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


def generalized_element_node(current: Node) -> Node:
    """The element node whose surface the values of ``current`` receive as points ``* -> K``.

    An object of ``C`` is a point ``* -> C``, so the surface is the one ``C``'s own
    placement gives to the points of its objects.  That placement is ``Cat()`` until
    ``Cat().Point(C)`` narrows it, and then the points of ``C`` are exactly the objects
    of ``C``: the level shift (D57, POL-CAT-083; ``specs/functor.md``, "The level
    shift").

    A morphism of ``C`` is a point ``* -> Mor(C)``, and a point of an object is a point
    of its own defining morphism.  Neither receives the level shift, which D57 states in
    those words, and the universal element node is the surface of both.  It is also
    ``Mor(C)``'s own until a point category narrows that, and asking ``C`` for ``Mor(C)``
    here would construct it inside ``C``'s own compile.
    """
    if current.role is Role.OBJECT:
        return node(current.category.category(), Role.ELEMENT)
    # ``Cat()`` compiling its own roles is the one moment there is no ``Cat()`` to name,
    # and the one category then is ``Cat()`` itself (``cat/category.py``, ``bootstrap``).
    universe = current.category.universe()
    return node(current.category if universe is None else universe, Role.ELEMENT)


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
        cat_element = generalized_element_node(current)
        for name, inherited in catalogue(cat_element).items():
            if name in entries and entries[name].owner is current.category and entries[name].role is current.role:
                continue
            entries[name] = _merge(entries[name], inherited) if name in entries else inherited
    catalogues[current.role] = entries
    return entries


def controlled_bases(current: Node) -> tuple[Node, ...]:
    """The distinct nodes one selected step from ``current``, most recently constructed first.

    The C3 merge takes the direct supers in the order of the total order, not in
    declaration order: Sage sorts them the same way (``Category._super_categories``
    applies ``Category._sort``, decreasing in ``_cmp_key``).  A category's ambient is
    declared first and constructed first, so declaration order is the wrong one here.
    The constructor walk still reads ``successors`` directly.

    The common ``Cat().ElementType`` node is not among them.  It is the preallocated end
    of every element chain, reached through the role's kernel class, so a selected
    functor into ``Cat()`` -- the monomorphism a point category declares -- adds no base at
    the element role and would place the chain end above its own descendants.
    """
    found: list[Node] = []
    for _, target in successors(current):
        if _is_cat_element_root(target):
            continue
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
        targets = controlled_bases(current)
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

    A node that reaches no other node ends on its role's kernel class.  These are the
    whole base list: the node's own written declaration is installed on the compiled
    class instead of standing among them (``_compiled_class``).
    """
    if _is_cat_element_root(current):
        return (CategoryPoint,)
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


# What a written class body states about its own source rather than about the
# mathematics.  ``dynamic_class`` sets each of these on the compiled class from ``doccls``.
_SOURCE_ATTRIBUTES = frozenset({
    "__dict__",
    "__weakref__",
    "__module__",
    "__doc__",
    "__qualname__",
    "__orig_bases__",
    "__type_params__",
    "__firstlineno__",
    "__static_attributes__",
})


def _rebound[**P, R](member: DeclaredMethod[P, R], compiled: type[CategoryPoint]) -> DeclaredMethod[P, R]:
    """A written member whose zero-argument ``super()`` names the class its body now runs in.

    A zero-argument ``super()`` reads the ``__class__`` cell CPython puts in the closure
    of a method defined in a class body, so a body installed on another class needs a
    cell naming that class.  ``attrs`` rewrites the same cell when it rebuilds a class
    with slots (``attr._make._ClassBuilder._create_slots_class``: "If a method mentions
    ``__class__`` or uses the no-arg ``super()``, the compiler will bake a reference to
    the class in the method itself"; inspected 2026-08-29).  It rewrites the one cell in
    place because one class replaces one class.  Here one written body serves a family of
    nodes and each node's ``super()`` is its own next step, so each node takes its own
    copy of the function with its own cell.
    """
    if isinstance(member, classmethod | staticmethod):
        return type(member)(_rebound(member.__func__, compiled))
    if not isinstance(member, FunctionType) or "__class__" not in member.__code__.co_freevars:
        return member
    closure = tuple(
        CellType(compiled) if name == "__class__" else cell
        for name, cell in zip(member.__code__.co_freevars, member.__closure__, strict=True)
    )
    rebound = FunctionType(member.__code__, member.__globals__, member.__name__, member.__defaults__, closure)
    rebound.__qualname__ = member.__qualname__
    rebound.__kwdefaults__ = member.__kwdefaults__
    rebound.__annotations__ = member.__annotations__
    rebound.__doc__ = member.__doc__
    return rebound


def _install_written_body(compiled: type[CategoryPoint], local: type[CategoryPoint]) -> None:
    """Put the node's written declaration onto its compiled class."""
    for name, member in vars(local).items():
        if name not in _SOURCE_ATTRIBUTES:
            setattr(compiled, name, _rebound(member, compiled))


def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: DeclaredMethod[P, R]) -> None:
    """Add one method to a declaration and to the class of every node already compiled from it.

    A compile installs the written body it reads (``_install_written_body``), so a
    declaration extended afterwards must reach the classes that copy is already in.  The
    axiom applications of ``Fun`` are the case: they are compiled when the class stating
    them is created, and the declaration they belong on is ``Cat()``'s morphism role,
    which the bootstrap compiled before that class could exist (POL-CAT-060, D89).

    The nodes are the ones the compiler linearized, which is every node it has built a
    class for.  ``install_level_shift`` writes onto live role classes the same way.
    """
    setattr(local, name, member)
    for found in _nodes_by_key.values():
        if found.category.local_role_class(found.role) is local:
            compiled = found.category.role_class(found.role)
            setattr(compiled, name, _rebound(member, compiled))


def _kernel_chain(last: Node) -> tuple[type, ...]:
    """The Python classes that follow the last node's compiled class in the MRO.

    A chain ends on the kernel class its last node stands on, which is the last node's
    role rather than the role the chain started in.  Two chains end elsewhere than on
    their own role's kernel class:

    * the shared ``Cat().ElementType`` root stands directly on ``CategoryPoint``, which
      every role's kernel class reaches through it;
    * a full subcategory of ``Mor(C)`` keeps the object role -- it is not itself a
      morphism category -- while its objects are the morphisms of ``C``, so its chain
      runs through ``(C, morphism)`` and ends on ``MorphismOfCategory``.

    A level shift contributes ``{C}``'s element class to ``C.ObjectType``, between that
    class and the kernel one (``install_level_shift``), so what follows a node compiled
    earlier is read off that node's own class rather than assumed.
    """
    if _is_cat_element_root(last):
        return CategoryPoint.__mro__
    return tuple(klass for klass in last.category.role_class(last.role).__mro__[1:] if klass is not Generic)


def _compiled_class(current: Node) -> type[CategoryPoint]:
    """The Sage-compiled implementation class of ``current``'s private runtime category."""
    return _runtime_category(current).parent_class


def borrowed_declaration(local: type[CategoryPoint]) -> type[CategoryPoint] | None:
    """The declaration ``local`` derives from, or ``None`` when it stands only on its role's kernel class.

    A written declaration states one category's mathematics and is installed on the class
    of the one node it belongs to (``_install_written_body``).  Deriving one from another
    would carry a second category's body onto that node, which is an implementation base
    that no structure functor supplies (POL-CAT-053, ``kernel/roles.py``).
    """
    for base in local.__mro__[1:]:
        if base is Generic or base in _KERNEL_CLASSES:
            return None
        return base
    return None


def _assert_linearized(current: Node, compiled: type[CategoryPoint]) -> None:
    """The MRO is the node linearization, ending on the kernel chain.

    Sage states the same invariant in ``Category._test_category_graph``
    (``sage/categories/category.py``): ``parent_class.mro()`` is the ancestors'
    compiled classes followed by the common Python chain end.  A written body is
    installed on the class of the one node it belongs to (POL-KERNEL-028), so it adds
    nothing to this order.

    PEP 695 puts ``typing.Generic`` in the bases of a parameterized declaration.  It
    names no node and carries no mathematics, so the order is read without it.
    """
    order = [] if _is_cat_element_root(current) else [_nodes_by_key[key] for key in _linearize(current)[0]]
    expected = [compiled]
    for found in order:
        expected.append(found.category.role_class(found.role))
    # A node reaching none stands on its role's kernel class, which is the whole chain;
    # ``_kernel_chain`` reads a node whose own class the compiler already installed.
    expected.extend(_kernel_chain(order[-1]) if order else CategoryPoint.__mro__ if _is_cat_element_root(current) else kernel_base(current.role).__mro__)
    expected = [klass for position, klass in enumerate(expected) if not any(later is klass for later in expected[position + 1 :])]
    actual = [klass for klass in compiled.__mro__ if klass is not Generic]
    assert actual == expected, (
        f"the {current.role.value} MRO of {current.category!r} is "
        f"{[klass.__qualname__ for klass in actual]}, expected "
        f"{[klass.__qualname__ for klass in expected]}"
    )


class _NodeRuntime(NamedTuple):
    initializer: FunctionType | None
    owner: type[CategoryPoint]


_node_runtimes: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


def _runtime(current: Node) -> _NodeRuntime:
    table = _node_runtimes[current.role]
    assert current.category in table, f"the {current.role.value} runtime of {current.category!r} is not compiled"
    return table[current.category]


def _advance(owner: type[CategoryPoint], instance: CategoryPoint) -> None:
    """Enter the next generated wrapper, or the kernel role initializer."""
    super(owner, instance).__init__()


def _object_step[Value: ObjectOfCategory, Datum](
    current: Node,
    construction_input: ObjectConstructionInput[Value, Datum],
    instance: ObjectOfCategory,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        if runtime.initializer is None:
            _advance(runtime.owner, instance)
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
            _advance(runtime.owner, instance)
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
            _advance(runtime.owner, instance)
            return
        runtime.initializer(instance, construction_input.datum)

    return initialize


def object_inputs[RootValue: ObjectOfCategory, RootDatum, Value: ObjectOfCategory, Datum](
    current: Node,
    root: ObjectConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, ObjectConstructionInput[Value, Datum]], ...]:
    """Each node ``current`` reaches, in ``reachable`` order, with its object input.

    The selected functor that first reaches a node converts the source input into the
    argument that node's initializer consumes.  A node several selected functors reach
    occurs once in the C3 linearization and runs one initializer through cooperative
    ``super()``, so one conversion is the whole requirement (POL-KERNEL-028/029).
    """
    assert current.role is Role.OBJECT
    found: list[tuple[Node, ObjectConstructionInput[Value, Datum]]] = [(current, root)]
    frontier = list(found)
    while frontier:
        source, source_input = frontier.pop(0)
        for functor, target in successors(source):
            if any(same_node(target, known) for known, _ in found):
                continue
            target_input = functor.object_constructor_input(source_input)
            # An object walk that reaches ``(Mor(C), object)`` is at the node
            # ``(C, morphism)``, whose values are morphisms and retain a morphism input
            # (POL-CAT-021).  The node's role names the input the step must supply.
            assert isinstance(target_input, _INPUT_TYPES[target.role]), (
                f"{functor!r} returned no {target.role.value} construction input for {target.category!r}"
            )
            found.append((target, target_input))
            frontier.append((target, target_input))
    return tuple(found)


def element_inputs[RootValue: CategoryPoint, RootDatum, Value: CategoryPoint, Datum](
    current: Node,
    root: ElementConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, ElementConstructionInput[Value, Datum]], ...]:
    """Each node ``current`` reaches, in ``reachable`` order, with its element input."""
    assert current.role is Role.ELEMENT
    found: list[tuple[Node, ElementConstructionInput[Value, Datum]]] = [(current, root)]
    frontier = list(found)
    while frontier:
        source, source_input = frontier.pop(0)
        for functor, target in successors(source):
            if any(same_node(target, known) for known, _ in found):
                continue
            target_input = functor.element_constructor_input(source_input)
            assert isinstance(target_input, ElementConstructionInput), f"{functor!r} returned no element construction input"
            found.append((target, target_input))
            frontier.append((target, target_input))
    return tuple(found)


def _object_steps[RootValue: ObjectOfCategory, RootDatum](
    current: Node,
    root: ObjectConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact object input into one zero-argument C3 node step."""
    found = object_inputs(current, root)
    for source, source_input in found:
        retain_constructed_transport(root, source.category, source_input)
    return tuple((source, _object_step(source, source_input, root.canonical_image)) for source, source_input in found)


def _element_steps[RootValue: CategoryPoint, RootDatum](
    current: Node,
    root: ElementConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact element input into one zero-argument C3 node step."""
    found = element_inputs(current, root)
    for source, source_input in found:
        retain_constructed_transport(root, source.category, source_input)
    return tuple((source, _element_step(source, source_input, root.canonical_image)) for source, source_input in found)


def _cat_element_step[Datum](
    root: ObjectConstructionInput[ObjectOfCategory, Datum] | MorphismConstructionInput[MorphismOfCategory, Datum],
) -> tuple[Node, Callable[[], None]]:
    """The point input ``* -> K`` at the common ``Cat().ElementType`` MRO root.

    A morphism of ``C`` is an object of ``Mor(C)`` and ``root.identity.category`` is that
    placement, so the object and morphism roles state one point (``specs/functor.md``,
    "Compiled implementation classes").
    """
    target = node(root.identity.category.universe(), Role.ELEMENT)
    point_input = ElementConstructionInput(root.canonical_image, CategoryPointIdentity(root.identity.category), None)
    return target, _element_step(target, point_input, root.canonical_image)


def _point_steps[Datum](
    root: ObjectConstructionInput[ObjectOfCategory, Datum],
    starts: tuple[Node, ...],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """The generalized-element chain of one object: every node the point ``* -> C`` it is runs.

    The chain always ends at the common ``Cat().ElementType`` root, which every role's
    kernel class reaches.  A level shift puts more above it: ``{C}``'s element class,
    carrying each point functor's target ``ElementType``, is contributed to
    ``C.ObjectType`` because the points ``* -> C`` are exactly the objects of ``C``
    (``install_level_shift``).  An object of a category with a selected functor into
    ``C`` is an object of ``C`` and carries that class too, so ``_point_starts`` reads
    every node the object walk reached whose class the shift entered.

    Every functor a point category selects is a subcategory monomorphism, identity on the
    shared values (``specs/functor.md``, "Point categories and point functors"), so the
    point is its own image at each target and the input does not change along the walk.
    The point carries no datum of its own: the value's construction data belongs to its
    own node in ``C``.
    """
    from sage_categories.kernel.refinement import traces_placement

    point_input = ElementConstructionInput(root.canonical_image, CategoryPointIdentity(root.identity.category), None)
    found: list[Node] = []
    for start in starts:
        if not any(same_node(start, known) for known in found):
            found.append(start)
    frontier = list(found)
    while frontier:
        source = frontier.pop(0)
        for functor, target in successors(source):
            if any(same_node(target, known) for known in found):
                continue
            assert traces_placement(functor), (
                f"{source.category!r} selects {functor!r}, which is no placement monomorphism, so it states "
                "no image of a point ``* -> C``"
            )
            found.append(target)
            frontier.append(target)
    return tuple((current, _element_step(current, point_input, root.canonical_image)) for current in found)


def _point_starts[Datum](
    root: ObjectConstructionInput[ObjectOfCategory, Datum],
    reached: tuple[Node, ...],
) -> tuple[Node, ...]:
    """Where the generalized-element chain of one object begins, per class the value carries.

    The common ``Cat().ElementType`` root is always one, and each node whose object class
    a level shift entered adds that point category's element node.  The condition is the
    class itself, so the steps are exactly the classes the value's MRO runs.
    """
    starts = [node(root.identity.category.universe(), Role.ELEMENT)]
    for current in reached:
        if current.role is not Role.OBJECT:
            continue
        point = current.category.universe().retained_point(current.category)
        if point is not None and issubclass(current.category.role_class(current.role), point.role_class(Role.ELEMENT)):
            starts.append(node(point, Role.ELEMENT))
    return tuple(starts)


def _element_cat_element_step[Value: CategoryPoint, Datum](
    root: ElementConstructionInput[Value, Datum],
) -> tuple[Node, Callable[[], None]]:
    """The defining-morphism input at the common ``Cat().ElementType`` MRO root."""
    assert isinstance(root.identity, ElementRoleIdentity)
    target = node(root.identity.defining_morphism.base_category().universe(), Role.ELEMENT)
    element_input = ElementConstructionInput(root.canonical_image, root.identity, None)
    return target, _element_step(target, element_input, root.canonical_image)


def morphism_inputs[RootValue: MorphismOfCategory, RootDatum, Value: MorphismOfCategory, Datum](
    current: Node,
    root: MorphismConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, MorphismConstructionInput[Value, Datum]], ...]:
    """Each node ``current`` reaches, in ``reachable`` order, with its morphism input."""
    assert current.role is Role.MORPHISM
    found: list[tuple[Node, MorphismConstructionInput[Value, Datum]]] = [(current, root)]
    frontier = list(found)
    while frontier:
        source, source_input = frontier.pop(0)
        for functor, target in successors(source):
            if any(same_node(target, known) for known, _ in found):
                continue
            target_input = functor.morphism_constructor_input(source_input)
            assert isinstance(target_input, MorphismConstructionInput), f"{functor!r} returned no morphism construction input"
            found.append((target, target_input))
            frontier.append((target, target_input))
    return tuple(found)


def _morphism_steps[RootValue: MorphismOfCategory, RootDatum](
    current: Node,
    root: MorphismConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each exact morphism input into one zero-argument C3 node step."""
    found = morphism_inputs(current, root)
    for source, source_input in found:
        retain_constructed_transport(root, source.category, source_input)
    return tuple((source, _morphism_step(source, source_input, root.canonical_image)) for source, source_input in found)


def _construct_object_root[Datum](
    current: Node,
    instance: ObjectOfCategory,
    identity: ObjectRoleIdentity,
    data: Datum,
) -> None:
    root = ObjectConstructionInput(instance, identity, data)
    retain_object_input(root)
    cat_element_identity = CategoryPointIdentity(identity.category)
    object_steps = _object_steps(current, root)
    steps = (*object_steps, *_point_steps(root, _point_starts(root, tuple(source for source, _ in object_steps))))
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
    cat_element_identity = CategoryPointIdentity(identity.category)
    steps = (*_morphism_steps(current, root), _cat_element_step(root))
    context = MorphismConstructionContext(root.canonical_image, root.identity, cat_element_identity, steps)
    token = activate_morphism_context(context)
    try:
        context.run(current)
        context.assert_complete()
    finally:
        deactivate_morphism_context(token)


def construct_category_singleton[Value: ObjectOfCategory](category_type: type[Value]) -> Value:
    """Allocate ``Cat()`` and start its provisional constructor chain inside its object context."""
    instance = category_type.__new__(category_type)
    identity = ObjectRoleIdentity(instance)
    root = ObjectConstructionInput(instance, identity, None)
    retain_object_input(root)
    cat_element_identity = CategoryPointIdentity(instance)
    cat_element_input = ElementConstructionInput(instance, cat_element_identity, None)
    retain_element_input(cat_element_input)
    context = ObjectConstructionContext(
        root.canonical_image,
        root.identity,
        cat_element_identity,
        (),
    )
    token = activate_object_context(context)
    try:
        category_type.__init__(instance)
        context.assert_complete()
    finally:
        deactivate_object_context(token)
    return instance


def _named_node(owner: Node, category: Category | None, role: Role) -> Node:
    """``owner``, checked against the category the caller named."""
    if category is None:
        return owner
    found = node(category, role)
    assert same_node(found, owner), f"the {role.value} class of {owner.category!r} cannot construct a value of {category!r}"
    return owner


def _object_wrapper(owner: Node) -> FunctionType:

    def initialize[Datum](
        instance: ObjectOfCategory,
        category: Category | None = None,
        data: Datum | None = None,
    ) -> None:
        active = active_construction_context(instance)
        if active is not None and active.canonical_image is instance:
            assert category is None and data is None, "an ancestor object constructor receives only its precomputed input"
            active.run(owner)
            return
        current = _named_node(owner, category, Role.OBJECT)
        identity = ObjectRoleIdentity(current.category)
        if data is None:
            _construct_object_root(current, instance, identity, None)
            return
        _construct_object_root(current, instance, identity, data)

    initialize.__name__ = "__init__"
    return initialize


def _element_wrapper(owner: Node) -> FunctionType:

    def initialize[Datum](
        instance: CategoryPoint,
        defining_morphism: MorphismOfCategory | None = None,
        data: Datum | None = None,
    ) -> None:
        active = active_construction_context(instance)
        if active is not None and active.canonical_image is instance:
            assert defining_morphism is None and data is None, "an ancestor element constructor receives only its precomputed input"
            active.run(owner)
            return
        assert defining_morphism is not None, "an element root constructor requires its defining morphism"
        _construct_element_root(owner, instance, ElementRoleIdentity(defining_morphism), data)

    initialize.__name__ = "__init__"
    return initialize


def _morphism_wrapper(owner: Node) -> FunctionType:

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
            active.run(owner)
            return
        assert category is not None and domain is not None and codomain is not None, (
            "a morphism root constructor requires its category and endpoints"
        )
        identity = MorphismRoleIdentity(category, domain, codomain)
        if data is None:
            _construct_morphism_root(owner, instance, identity, None)
            return
        _construct_morphism_root(owner, instance, identity, data)

    initialize.__name__ = "__init__"
    return initialize


def _constructor_wrapper(role: Role, owner: Node) -> FunctionType:
    match role:
        case Role.OBJECT:
            return _object_wrapper(owner)
        case Role.ELEMENT:
            return _element_wrapper(owner)
        case Role.MORPHISM:
            return _morphism_wrapper(owner)
    raise AssertionError(role)


def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile the three role classes of ``category`` from its local declarations and its selected functors."""
    for functor in functors:
        functor_category = category.category().morphism_category(1)
        assert functor in functor_category, f"{functor!r} is not an object of {functor_category!r}"
        assert functor.domain() is category, f"{functor!r} does not have domain {category!r}"
        # Naming a declared category as a functor's *domain* is always safe; selecting a
        # functor into one that no implementation claims is not, because the declaration's
        # empty implementation classes would compile into this category's own
        # linearization (``specs/functor.md``, "Failing loudly").
        open_codomain = category.universe().open_declaration(functor.codomain())
        assert open_codomain is None, (
            f"{category!r} selects {functor!r} into {open_codomain}, which Cat declares and no implementation claims"
        )
    assert all(first is not second for index, first in enumerate(functors) for second in functors[index + 1 :]), (
        f"{category!r} selects one functor twice"
    )
    category.select_functors(functors)
    for role in _COMPILE_ORDER:
        _assert_acyclic(node(category, role), ())
    for role in _COMPILE_ORDER:
        current = node(category, role)
        if current.category is not category:
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        # Catalogue construction rejects semantic collisions.  Inherited execution
        # itself is ordinary Python lookup through Sage's controlled compiled MRO.
        catalogue(current)
        compiled = _compiled_class(current)
        # The generated wrapper owns the private direct-source initialization protocol.
        node_initializer = vars(compiled).get("__init__")
        if _is_cat_element_root(current):
            install_cat_element_root(compiled)
        compiled.__init__ = _constructor_wrapper(role, current)
        _node_runtimes[role][category] = _NodeRuntime(node_initializer, compiled)
        setattr(category, role.value, compiled)


def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile ``category`` again after an implementation claimed the declaration it is (D80).

    The declared object is the final object, so this compiles onto the one already in
    ``Cat()``: the ordinal is not retaken, and the cached linearizations and method
    catalogues are this compile's own outputs, so they are dropped and rebuilt.
    """
    for role in Role:
        table = _linearizations[role]
        if category in table:
            del table[category]
    category.catalogues().clear()
    compile_category(category, functors)


def install_level_shift(point: Category) -> None:
    """Contribute ``{C}``'s element class to ``C.ObjectType``, whose values are the points of ``C``.

    The member of a point category is a category ``C`` exactly when the level shift
    applies.  The points ``* -> C`` are then exactly the objects of ``C``, so the class
    ``{C}`` compiled for its element role -- carrying each point functor's target
    ``D.ElementType`` -- is a class of an object of ``C``.  The object role is the only
    one it reaches: ``D.ObjectType`` applies to the category ``C``, which
    ``Cat().Point`` refines into ``{C}``, and ``D.MorphismType`` to ``{C}.MorphismType``,
    whose sole value is ``1_C`` and which ``{C}``'s own compile builds.  Morphisms of
    ``C`` receive no element surface (D57, POL-CAT-083; ``specs/functor.md``, "The level
    shift").

    The level shift adds the selected target class to the live ``C.ObjectType``.
    It then initializes that private class state for objects built before the shift.
    """
    member = point.member()
    if member not in point.universe():
        return
    current = node(member, Role.OBJECT)
    role_class = current.category.role_class(current.role)
    shifted_class = point.role_class(Role.ELEMENT)
    if issubclass(role_class, shifted_class):
        return
    universal = catalogue(node(member.universe(), Role.ELEMENT))
    shifted = catalogue(node(point, Role.ELEMENT))
    # The member's object catalogue is recomputed because its generalized-element node is
    # now ``{C}``'s: the merge is what rejects a spelling the shift and the member both
    # declare.
    current.category.catalogues().pop(current.role, None)
    compiled = catalogue(current)
    for name, entry in shifted.items():
        if universal.get(name) is entry:
            continue
        assert compiled[name] is entry, (
            f"{name!r} is declared both by {compiled[name].owner!r} and by the level shift from {point!r}; "
            "name the two mathematical operations distinctly"
        )
    role_class.__bases__ = (*role_class.__bases__, shifted_class)
    for constructed in _placed_objects(member):
        _initialize_level_shift(node(point, Role.ELEMENT), constructed)


def _placed_objects(category: Category) -> tuple[ObjectOfCategory, ...]:
    """The objects of ``category`` the kernel has built, each once.

    Every object walk retains its input at each node it reaches, keyed by the source
    value and indexed by the target category (``retain_constructed_transport``), so this
    table is the objects of ``category`` that are still live: its keys are weak, and an
    object nothing holds is gone.
    """
    table = canonical_images[Role.OBJECT]
    if category not in table:
        return ()
    found: list[ObjectOfCategory] = []
    for _, image in table[category].items():
        if isinstance(image, ObjectOfCategory) and not any(image is known for known in found):
            found.append(image)
    return tuple(found)


def _initialize_level_shift(start: Node, value: ObjectOfCategory) -> None:
    """Run the shift's element chain on one object built before the shift.

    The classes above ``{C}.ElementType`` in the value's MRO ran when it was built, so the
    chain resumes at the class the shift contributed and runs down to the common
    ``Cat().ElementType`` root, which is where its steps end.
    """
    root = retained_object_input(value)
    steps = _point_steps(root, (start,))
    context = ObjectConstructionContext(value, root.identity, CategoryPointIdentity(root.identity.category), steps)
    token = activate_object_context(context)
    try:
        context.run(start)
        context.assert_complete()
    finally:
        deactivate_object_context(token)
