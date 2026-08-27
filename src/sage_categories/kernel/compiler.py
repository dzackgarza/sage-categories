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

The compiled role class is a Sage dynamic class (``sage.structure.dynamic_class``).
Its bases are exactly the *controlled* direct bases that
``sage.misc.c3_controlled.C3_sorted_merge`` returns for the node: compiled classes of
reachable nodes.  A node that reaches none ends its chain on the kernel role class its
declaration stands on: ``Category`` for the category role, ``ObjectOfCategory``,
``ElementOfObject``, or ``MorphismOfCategory`` below the rest.

A declaration is never a base.  It is passed as ``cls``, so its methods are inserted
into the compiled class and its own Python bases are dropped.  This is Sage's
``Category._make_named_class``, which passes ``ParentMethods`` the same way and warns
when a method provider has a super class at all.

That is what lets Python linearize the result.  ``C3_sorted_merge`` orders *nodes*;
every class it never sees is unconstrained, and Python then places it wherever each
individual class construction allows.  Two constructions rank one such pair opposite
ways, and a node reaching both has no MRO at all.  With declarations out of the bases,
every class in every compiled MRO is a node class or a chain end, and carries the node
order; ``_assert_linearized`` holds that.  Method compilation constructs no value image
(POL-KERNEL-001).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import CellType, FunctionType
from typing import TYPE_CHECKING, Any, Concatenate, Generic, NamedTuple

from sage.misc.c3_controlled import C3_sorted_merge
from sage.structure.dynamic_class import dynamic_class

import sage_categories.kernel.descriptors as descriptors
from sage_categories.kernel.caches import MonoDict
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role, kernel_base

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "DeclaredMethod",
    "Entry",
    "Node",
    "Route",
    "SemanticCollisionError",
    "Step",
    "StructuralImageMismatch",
    "catalogue",
    "compile_category",
    "controlled_bases",
    "empty_local_role",
    "local_methods",
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


class Step(NamedTuple):
    """One selected structural step: a functor, the roles at its two ends, and the stage it applies to.

    The two roles differ only for a level shift, where no functor acts and ``functor`` is
    ``None``: the objects of a category ``C`` are the stage-``1`` generalized elements of
    ``C``, and its morphisms the stage-``[1]`` ones (``specs/functor.md``, "The level
    shift").  ``stage`` restricts a step to the values at one stage and is ``None`` for
    every ordinary step, which acts on its source role at every stage.
    """

    functor: Functor | None
    source_role: Role
    target_role: Role
    stage: ObjectOfCategory | None


type Route = tuple[Step, ...]

# A declaring method: its receiver is a value of the declaring role class, and its
# remaining parameters and result are exactly those of its typed signature
# (POL-CAT-075, POL-TYPE-028).
type DeclaredMethod[**P, R] = Callable[Concatenate[CategoryPoint, P], R]

# One entry of a class body: a function, a descriptor, a nested class, or a constant.
# ``vars`` is Python's own introspection of a namespace and admits every value, so the
# ambiguity is genuine and named once here (POL-TYPE-004).
type ClassBodyValue = Any


class Entry[**P, R](NamedTuple):
    """One compiled method: its declaring owner and role, its spelling, its declaration, and its execution route."""

    owner: Category
    role: Role
    name: str
    function: DeclaredMethod[P, R]
    route: Route


_IGNORED_NAMES = frozenset(
    {
        "__init__",
        "__new__",
        "__repr__",
        "__init_subclass__",
        "__class_getitem__",
        # The role accessors.  Every kernel role class defines its own, and the compiler
        # itself calls them to find a value's placement, so a forwarded copy would call
        # the very accessor it is trying to transport for.  ``Cat().ElementType``
        # declares all three, and its element node is reachable from a point category's.
        "stage",
        "parent",
        "defining_morphism",
    }
)

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
    return (*_functor_steps(current), *_level_shift(current))


def _functor_steps(current: Node) -> tuple[tuple[Step, Node], ...]:
    return tuple(
        (Step(functor, current.role, current.role, None), node(functor.codomain(), current.role))
        for functor in current.category.selected_functors()
    )


def _level_shift(current: Node) -> tuple[tuple[Step, Node], ...]:
    """The step from a category's objects or morphisms to the elements of its point category.

    ``{C}``'s sole object is the category ``C``, and its generalized elements are the
    objects of ``C`` at stage ``1`` and the morphisms of ``C`` at stage ``[1]``
    (``specs/functor.md``, "The level shift").  So a surface reaching ``{C}.ElementType``
    reaches ``C.ObjectType`` and ``C.MorphismType``, split by stage.

    No functor acts: the value of the step is the value's own defining morphism, which
    the kernel already retains.  The step is therefore not a subcategory relation and
    contributes no class base -- see ``_selected_targets``.
    """
    import sage_categories.cat.category as category_module

    # ``Cat()`` compiles its own roles before the singleton is bound, and no point
    # category can exist before it: the table is empty until then.
    universe = category_module._CAT
    if universe is None or current.role not in (Role.OBJECT, Role.MORPHISM):
        return ()
    point = universe.retained_point(current.category)
    if point is None:
        return ()
    stage = universe.Terminal() if current.role is Role.OBJECT else universe.Simplex(1)
    return ((Step(None, current.role, Role.ELEMENT, stage), node(point, Role.ELEMENT)),)


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


def local_methods[**P, R](local_class: type[CategoryPoint]) -> dict[str, DeclaredMethod[P, R]]:
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
        for name, function in local_methods(local_class).items()
    }
    for step, target in successors(current):
        for name, inherited in catalogue(target).items():
            if name in entries and not entries[name].route:
                continue
            candidate = inherited._replace(route=(step, *inherited.route))
            entries[name] = _merge(entries[name], candidate) if name in entries else candidate
    catalogues[current.role] = entries
    return entries


def _chain_end_classes() -> tuple[type, ...]:
    """The classes a chain of any role may end in, most specific first.

    ``Category`` ends the chain of the category role.  It is ``Cat().ObjectType``'s own
    declaration and the class every category is an instance of: a category is built from
    its own hand-written ``Category`` subclass and never from a compiled class
    (``refinement.place``), so those subclasses must be able to override its methods,
    which only inheritance gives them.  The three kernel role classes end the other
    chains the same way.  ``Generic`` and ``object`` are Python's, below all of them.
    """
    from sage_categories.cat.category import Category

    return (Category, kernel_base(Role.OBJECT), kernel_base(Role.ELEMENT), kernel_base(Role.MORPHISM), CategoryPoint, Generic, object)


def install_level_shift(member: Category) -> None:
    """Install a point category's element surface on its member's objects and morphisms.

    ``{C}`` is constructed after ``C``, so ``C``'s roles were compiled before the level
    shift existed.  The shift only adds inherited spellings, so they go onto the classes
    that are already there.  Recompiling ``C`` instead would build *new* role classes
    while every already-compiled descendant kept the previous ones as bases, and those
    would then stand for no node.

    Installing rather than rebuilding also means the values of ``C`` that already exist
    gain the surface, since they are instances of these very classes.
    """
    for role in (Role.OBJECT, Role.MORPHISM):
        current = node(member, role)
        current.category.catalogues().pop(current.role, None)
        role_class = current.category.role_class(current.role)
        for step, target in _level_shift(current):
            for name, inherited in catalogue(target).items():
                if name in vars(role_class):
                    continue
                entry = inherited._replace(route=(step, *inherited.route))
                setattr(role_class, name, descriptors.forwarding_descriptor(entry))


def _kernel_base_of(klass: type[CategoryPoint]) -> type[CategoryPoint]:
    """The kernel role class a role class stands on: the end of its chain."""
    return next(found for found in klass.__mro__ if found in _chain_end_classes())


def empty_local_role(category: Category, role: Role) -> type[CategoryPoint]:
    """The local role class that declares nothing, on the kernel base of the ambient's role.

    One class per category and role, retained: it names the declaring owner of the node
    for ``descriptors._declared``, and a node that reaches no other node reads its
    kernel base off it (POL-CAT-016, POL-CAT-011).
    """
    table = _empty_local_roles[role]
    if category not in table:
        ambient_node = node(category.ambient(), role)
        base = _kernel_base_of(ambient_node.category.role_class(ambient_node.role))
        table[category] = type(f"{category!r}.{role.value}", (base,), {})
    return table[category]


def _selected_targets(current: Node) -> tuple[Node, ...]:
    """The distinct nodes one selected step from ``current``, most recently constructed first.

    The C3 merge takes the direct supers in the order of the total order, not in
    declaration order: Sage sorts them the same way (``Category._super_categories``
    applies ``Category._sort``, decreasing in ``_cmp_key``).  A category's ambient is
    declared first and constructed first, so declaration order is the wrong one here.
    Only the functor steps appear here.  A level shift is not a subcategory relation, so
    it contributes no base; and it points from a category to its *newer* point category,
    which would break the total order the controlled merge is built on -- a node must
    rank strictly above every node it reaches.  The shift carries methods through the
    catalogue instead, which needs no such order.

    Route order and catalogue precedence still read ``successors`` directly.
    """
    found: list[Node] = []
    for _, target in _functor_steps(current):
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


def controlled_bases(current: Node) -> tuple[Node, ...]:
    """The nodes whose classes are the direct bases of ``current``'s compiled class.

    The controlled list ``C3_sorted_merge`` returns: the selected targets together
    with whatever control edges the merge needed, in the order Python must see
    them.  Declaration order is not that order -- a category's ambient is declared
    first and constructed first, so a base list in declaration order can put a
    class above its own descendant, which has no linearization at all.
    """
    return tuple(_nodes_by_key[key] for key in _linearize(current)[1])


def _base_classes(current: Node, local: type[CategoryPoint]) -> tuple[type[CategoryPoint], ...]:
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

    A node that reaches no other node is the end of its chain, and its base is the kernel
    role class its declaration stands on.  A declaration is never a base itself: it
    belongs to one node, but two chain ends put two declarations directly above one
    kernel role class, and nothing then orders those two against each other.
    """
    keys = _linearize(current)[1]
    classes = [_nodes_by_key[key].category.role_class(_nodes_by_key[key].role) for key in keys]
    bases = [klass for position, klass in enumerate(classes) if not any(later is klass for later in classes[position + 1 :])]
    if not bases:
        bases = [_kernel_base_of(local)]
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


def _declaration_methods(local: type[CategoryPoint], cell: CellType) -> dict[str, ClassBodyValue]:
    """The complete class body of a local declaration, ready to be inserted into a compiled class."""
    namespace: dict[str, ClassBodyValue] = {}
    for name, value in vars(local).items():
        if name in ("__dict__", "__weakref__", "__qualname__"):
            continue
        uses_super = isinstance(value, FunctionType) and "__class__" in value.__code__.co_freevars
        namespace[name] = _rebound(value, cell) if uses_super else value
    return namespace


def _assert_linearized(current: Node, compiled: type[CategoryPoint]) -> None:
    """The compiled class's MRO carries the reachable nodes' classes in linearization order.

    Sage states the same invariant in ``Category._test_category_graph``
    (``sage/categories/category.py``): ``parent_class.mro()`` is the ancestors'
    compiled classes followed by ``object``.  The MRO here is exactly that, plus the
    kernel role class the chain ends in.  Nothing else may appear: a class the node
    order does not rank is free to sit anywhere, two class constructions then rank one
    such pair opposite ways, and a node reaching both has no linearization at all.
    That failure surfaces far from its cause, so the condition is checked here.
    """
    order = [_nodes_by_key[key] for key in _linearize(current)[0]]
    classes = [found.category.role_class(found.role) for found in order]
    positions = {klass: position for position, klass in enumerate(compiled.mro())}
    ranked = {*classes, compiled, *_chain_end_classes()}
    unranked = [klass for klass in compiled.mro() if klass not in ranked]
    assert not unranked, (
        f"the {current.role.value} class of {current.category!r} carries "
        f"{unranked[0].__name__}, which stands for no node and which the node order "
        "therefore does not rank"
    )
    missing = [found for found, klass in zip(order, classes) if klass not in positions]
    assert not missing, (
        f"the {current.role.value} class of {current.category!r} does not carry "
        f"{missing[0].category!r}.{missing[0].role.value}, which it reaches"
    )
    placed = [(found, positions[klass]) for found, klass in zip(order, classes)]
    inverted = next(((first, second) for (first, a), (second, b) in zip(placed, placed[1:]) if a > b), None)
    assert inverted is None, (
        f"the {current.role.value} class of {current.category!r} puts "
        f"{inverted[1].category!r}.{inverted[1].role.value} before "
        f"{inverted[0].category!r}.{inverted[0].role.value}, against the C3 order; "
        "one class stands for two nodes"
    )


def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile the three role classes of ``category`` from its local declarations and its selected functors."""
    for functor in functors:
        functor_category = category.universe().morphism_category(1)
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
        bases = _base_classes(current, local)
        cell = CellType()
        # The declaration supplies its methods by inheritance when it is the kernel role
        # class that ends the chain, and by copy otherwise.  Copying ``Category`` onto
        # ``Cat().ObjectType`` would shadow the overrides of its own Python subclasses,
        # which are the classes categories are built from (``refinement.place``).
        namespace = dict(surface) if local in bases else {**surface, **_declaration_methods(local, cell)}
        try:
            compiled = dynamic_class(
                f"{category!r}.{role.value}",
                bases,
                cls=type(local.__name__, (), namespace),
                doccls=local,
                prepend_cls_bases=False,
            )
        except TypeError as conflict:
            raise TypeError(
                f"the {role.value} class of {category!r} has no linearization over "
                f"{[klass.__name__ for klass in bases]}: {conflict}"
            ) from conflict
        cell.cell_contents = compiled
        setattr(category, role.value, compiled)
        _assert_linearized(current, compiled)
