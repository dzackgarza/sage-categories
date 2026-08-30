"""Compile local declarations and selected target classes for the current kernel."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import CellType, FunctionType, GenericAlias
from typing import TYPE_CHECKING, Concatenate, Generic, NamedTuple

from sage.categories.category import Category as SageCategory
from sage.misc.lazy_attribute import lazy_attribute
from sage.structure.coerce_dict import MonoDict

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
    retained_object_inputs,
    _retain_initializer_invocation,
    _retained_initializer_replays,
)
from sage_categories.kernel.roles import (
    CategoryPoint,
    MorphismOfCategory,
    ObjectOfCategory,
    Role,
    building_role_classes,
    install_cat_element_root,
    kernel_base,
)

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "Node",
    "SemanticCollisionError",
    "compile_category",
    "install_level_shift",
    "install_on_declaration",
    "node",
    "recompile_category",
    "same_node",
]


class SemanticCollisionError(Exception):
    """Two incomparable owners declare one method spelling (POL-CAT-011, POL-API-011)."""


class _KernelRoleRootCategory(SageCategory):
    """A private Sage category for the final implementation class of one role."""

    def __init__(self, role: Role, root: type[CategoryPoint]) -> None:
        self._role = role
        self._root = root
        super().__init__()

    @property
    def _cmp_key(self) -> tuple[int, int]:
        return (0, _ROLE_POSITIONS[self._role] - len(Role))

    def super_categories(self) -> list[SageCategory]:
        return []

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        return self._root


class _RuntimeImplementationCategory(SageCategory):
    """A private Sage category whose ``parent_class`` is one owned implementation role."""

    def __init__(self, current: Node, targets: tuple[SageCategory, ...]) -> None:
        self._current = current
        self._targets = targets
        self.ParentMethods = current.category.local_role_class(current.role)
        super().__init__()

    @property
    def _cmp_key(self) -> tuple[int, int]:
        return (0, node_key(self._current))

    def super_categories(self) -> list[SageCategory]:
        return list(self._targets)

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        return self._make_named_class("parent_class", "ParentMethods", cache=True)


class Node(NamedTuple):
    category: Category
    role: Role


_runtime_categories: dict[Role, MonoDict] = {role: MonoDict() for role in Role}
_kernel_role_roots: dict[tuple[Role, type[CategoryPoint]], _KernelRoleRootCategory] = {}


def _role_root(role: Role, root: type[CategoryPoint]) -> _KernelRoleRootCategory:
    """The identity-cached private Sage category ending one role chain at ``root``."""
    key = (role, root)
    if key not in _kernel_role_roots:
        _kernel_role_roots[key] = _KernelRoleRootCategory(role, root)
    return _kernel_role_roots[key]


def _kernel_role_root(role: Role) -> _KernelRoleRootCategory:
    """The identity-cached private Sage category for one kernel role root."""
    return _role_root(role, kernel_base(role))


def _cat_element_role_root() -> _KernelRoleRootCategory:
    """The root below the first compiled ``Cat().ElementType`` class."""
    return _role_root(Role.ELEMENT, CategoryPoint)


_IGNORED_NAMES = frozenset({"__init__", "__new__", "__repr__", "__init_subclass__", "__class_getitem__"})

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


def _runtime_category(current: Node) -> _RuntimeImplementationCategory:
    """The identity-cached Sage category that owns ``current``'s compiled role class."""
    table = _runtime_categories[current.role]
    if current.category in table:
        return table[current.category]
    targets: tuple[SageCategory, ...] = tuple(_runtime_category(target) for _, target in successors(current))
    if not targets:
        targets = (_cat_element_role_root() if _is_cat_element_root(current) else _kernel_role_root(current.role),)
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
        for functor in current.category.structure_functors()
    )


def _local_method_names(local_class: type[CategoryPoint]) -> tuple[str, ...]:
    """The public method spellings written on one local declaration."""
    return tuple(
        name
        for name, function in vars(local_class).items()
        if inspect.isfunction(function) and name not in _IGNORED_NAMES and (not name.startswith("_") or name.startswith("__"))
    )


def _rebound[**P, R](member: Callable[Concatenate[CategoryPoint, P], R], compiled: type[CategoryPoint]) -> Callable[Concatenate[CategoryPoint, P], R]:
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
    """Rebind each copied method whose zero-argument ``super()`` names ``local``."""
    if Generic in local.__mro__:
        compiled.__class_getitem__ = classmethod(GenericAlias)
    for name, member in vars(local).items():
        if isinstance(member, classmethod | staticmethod | FunctionType):
            setattr(compiled, name, _rebound(member, compiled))


def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: Callable[Concatenate[CategoryPoint, P], R]) -> None:
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
    for table in _runtime_categories.values():
        for _, runtime in table.items():
            if runtime._current.category.local_role_class(runtime._current.role) is local:
                compiled = runtime.parent_class
                setattr(compiled, name, _rebound(member, compiled))


def _compiled_class(current: Node) -> type[CategoryPoint]:
    """The Sage-compiled implementation class of ``current``'s private runtime category."""
    with building_role_classes():
        compiled = _runtime_category(current).parent_class
    _install_written_body(compiled, current.category.local_role_class(current.role))
    return compiled


def _assert_no_semantic_collisions(*surfaces: type[CategoryPoint]) -> None:
    """Reject one public spelling from incomparable owners in Sage's compiled MROs."""
    runtime_by_class = {
        runtime.__dict__["parent_class"]: runtime
        for table in _runtime_categories.values()
        for _, runtime in table.items()
        if "parent_class" in runtime.__dict__
    }
    owners: dict[str, tuple[Node, type[CategoryPoint]]] = {}
    for surface in surfaces:
        for implementation in surface.__mro__:
            runtime = runtime_by_class.get(implementation)
            if runtime is None:
                continue
            for name in _local_method_names(runtime.ParentMethods):
                previous = owners.get(name)
                if previous is None:
                    owners[name] = (runtime._current, implementation)
                    continue
                previous_node, previous_class = previous
                if issubclass(implementation, previous_class) or issubclass(previous_class, implementation):
                    continue
                raise SemanticCollisionError(
                    f"{name!r} is declared by both {previous_node.category!r} and {runtime._current.category!r}, "
                    "which are incomparable; name the two mathematical operations distinctly"
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


type InitializerReplay = Callable[[CategoryPoint], None]
type InitializerReplayLookup = Callable[[], dict[SageCategory, InitializerReplay]]


def _target_replays(
    current: Node,
    images: tuple[CategoryPoint, ...],
) -> dict[SageCategory, InitializerReplay]:
    """Target initializers keyed by runtime category; Sage C3 orders their execution."""
    applicable = {
        runtime
        for runtime in _runtime_category(current)._all_super_categories
        if isinstance(runtime, _RuntimeImplementationCategory)
    }
    replays: dict[SageCategory, InitializerReplay] = {}
    for image in images:
        for runtime_category, replay in _retained_initializer_replays(image):
            if runtime_category in applicable:
                replays.setdefault(runtime_category, replay)
    return replays


def _empty_initializer_replays() -> dict[SageCategory, InitializerReplay]:
    return {}


def _deferred_target_replays(
    current: Node,
    images: Callable[[], tuple[CategoryPoint, ...]],
) -> InitializerReplayLookup:
    """Construct public target images when the source initializer first enters an inherited node."""
    replays: dict[SageCategory, InitializerReplay] | None = None

    def lookup() -> dict[SageCategory, InitializerReplay]:
        nonlocal replays
        if replays is None:
            replays = _target_replays(current, images())
        return replays

    return lookup


def _object_target_images(current: Node, source: ObjectOfCategory) -> tuple[CategoryPoint, ...]:
    """The ordinary public object images of ``current``'s immediate selected functors."""
    return tuple(functor.on_object(source) for functor, _ in successors(current))


def _element_target_images(current: Node, defining_morphism: MorphismOfCategory) -> tuple[CategoryPoint, ...]:
    """The ordinary public element images of ``current``'s immediate selected functors."""
    return tuple(
        functor.codomain().element_from_defining_morphism(functor.on_morphism(defining_morphism))
        for functor, _ in successors(current)
    )


def _morphism_target_images(current: Node, source: MorphismOfCategory) -> tuple[CategoryPoint, ...]:
    """The ordinary public morphism images of ``current``'s immediate selected functors."""
    return tuple(functor.on_morphism(source) for functor, _ in successors(current))


def _linearized_nodes(current: Node) -> tuple[Node, ...]:
    """The selected target nodes in the private Sage category's C3 order."""
    return tuple(
        runtime._current
        for runtime in _runtime_category(current)._all_super_categories
        if isinstance(runtime, _RuntimeImplementationCategory)
    )


def _object_step[Value: ObjectOfCategory, Datum](
    current: Node,
    construction_input: ObjectConstructionInput[Value, Datum],
    instance: ObjectOfCategory,
    replays: InitializerReplayLookup,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        replay = replays().get(_runtime_category(current))
        if replay is not None:
            replay(instance)
            return
        if runtime.initializer is None:
            _advance(runtime.owner, instance)
            return
        _retain_initializer_invocation(instance, _runtime_category(current), runtime.initializer, construction_input.datum)
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _element_step[Value: CategoryPoint, Datum](
    current: Node,
    construction_input: ElementConstructionInput[Value, Datum],
    instance: Value,
    replays: InitializerReplayLookup,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        replay = replays().get(_runtime_category(current))
        if replay is not None:
            replay(instance)
            return
        if runtime.initializer is None:
            _advance(runtime.owner, instance)
            return
        _retain_initializer_invocation(instance, _runtime_category(current), runtime.initializer, construction_input.datum)
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _morphism_step[Value: MorphismOfCategory, Datum](
    current: Node,
    construction_input: MorphismConstructionInput[Value, Datum],
    instance: MorphismOfCategory,
    replays: InitializerReplayLookup,
) -> Callable[[], None]:
    runtime = _runtime(current)

    def initialize() -> None:
        replay = replays().get(_runtime_category(current))
        if replay is not None:
            replay(instance)
            return
        if runtime.initializer is None:
            _advance(runtime.owner, instance)
            return
        _retain_initializer_invocation(instance, _runtime_category(current), runtime.initializer, construction_input.datum)
        runtime.initializer(instance, construction_input.datum)

    return initialize


def _object_steps[RootValue: ObjectOfCategory, RootDatum](
    current: Node,
    root: ObjectConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each object C3 node into one zero-argument initialization step."""
    replays = _deferred_target_replays(current, lambda: _object_target_images(current, root.canonical_image))
    return (
        (current, _object_step(current, root, root.canonical_image, _empty_initializer_replays)),
        *(
            (source, _object_step(source, root, root.canonical_image, replays))
            for source in _linearized_nodes(current)
        ),
    )


def _element_steps[RootValue: CategoryPoint, RootDatum](
    current: Node,
    root: ElementConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each element C3 node into one zero-argument initialization step."""
    assert isinstance(root.identity, ElementRoleIdentity)
    replays = _deferred_target_replays(current, lambda: _element_target_images(current, root.identity.defining_morphism))
    return (
        (current, _element_step(current, root, root.canonical_image, _empty_initializer_replays)),
        *(
            (source, _element_step(source, root, root.canonical_image, replays))
            for source in _linearized_nodes(current)
        ),
    )


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
    return target, _element_step(target, point_input, root.canonical_image, _empty_initializer_replays)


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
    return tuple(
        (current, _element_step(current, point_input, root.canonical_image, _empty_initializer_replays))
        for current in found
    )


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
    return target, _element_step(target, element_input, root.canonical_image, _empty_initializer_replays)


def _morphism_steps[RootValue: MorphismOfCategory, RootDatum](
    current: Node,
    root: MorphismConstructionInput[RootValue, RootDatum],
) -> tuple[tuple[Node, Callable[[], None]], ...]:
    """Close each morphism C3 node into one zero-argument initialization step."""
    replays = _deferred_target_replays(current, lambda: _morphism_target_images(current, root.canonical_image))
    return (
        (current, _morphism_step(current, root, root.canonical_image, _empty_initializer_replays)),
        *(
            (source, _morphism_step(source, root, root.canonical_image, replays))
            for source in _linearized_nodes(current)
        ),
    )


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


def _construction_node(instance: CategoryPoint, role: Role) -> Node:
    """The compiled node whose direct role class constructed ``instance``."""
    by_class = {runtime.owner: Node(category, role) for category, runtime in _node_runtimes[role].items()}
    current = next((by_class[base] for base in type(instance).__mro__ if base in by_class), None)
    assert current is not None, f"{type(instance)!r} has no compiled {role.value} class"
    return current


def _initialize_object[Datum](
    instance: ObjectOfCategory,
    category: Category | None = None,
    data: Datum | None = None,
) -> None:
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        assert category is None and data is None, "an ancestor object constructor receives only its precomputed input"
        active.advance()
        return
    current = _construction_node(instance, Role.OBJECT)
    if category is not None:
        assert same_node(node(category, Role.OBJECT), current), (
            f"the ObjectType class of {current.category!r} cannot construct a value of {category!r}"
        )
    _construct_object_root(current, instance, ObjectRoleIdentity(current.category), data)


def _initialize_element[Datum](
    instance: CategoryPoint,
    defining_morphism: MorphismOfCategory | None = None,
    data: Datum | None = None,
) -> None:
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        assert defining_morphism is None and data is None, "an ancestor element constructor receives only its precomputed input"
        active.advance()
        return
    assert defining_morphism is not None, "an element root constructor requires its defining morphism"
    current = _construction_node(instance, Role.ELEMENT)
    _construct_element_root(current, instance, ElementRoleIdentity(defining_morphism), data)


def _initialize_morphism[Datum](
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
        active.advance()
        return
    assert category is not None and domain is not None and codomain is not None, (
        "a morphism root constructor requires its category and endpoints"
    )
    current = _construction_node(instance, Role.MORPHISM)
    _construct_morphism_root(current, instance, MorphismRoleIdentity(category, domain, codomain), data)


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
    for role in _COMPILE_ORDER:
        current = node(category, role)
        if current.category is not category:
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        compiled = _compiled_class(current)
        _assert_no_semantic_collisions(compiled)
        # The compiler owns the private direct-source initialization protocol.
        node_initializer = vars(compiled).get("__init__")
        if _is_cat_element_root(current):
            install_cat_element_root(compiled)
        match role:
            case Role.OBJECT:
                compiled.__init__ = _initialize_object
            case Role.ELEMENT:
                compiled.__init__ = _initialize_element
            case Role.MORPHISM:
                compiled.__init__ = _initialize_morphism
        _node_runtimes[role][category] = _NodeRuntime(node_initializer, compiled)
        setattr(category, role.value, compiled)


def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile ``category`` again after an implementation claims its declaration (D80)."""
    for role in Role:
        table = _runtime_categories[role]
        if category in table:
            del table[category]
        runtimes = tuple(runtime for _, runtime in table.items())
        for runtime in runtimes:
            for name in (
                "parent_class",
                "_all_super_categories",
                "_all_super_categories_proper",
                "_set_of_super_categories",
                "_super_categories",
                "_super_categories_for_classes",
            ):
                runtime.__dict__.pop(name, None)
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
    _assert_no_semantic_collisions(role_class, shifted_class)
    role_class.__bases__ = (*role_class.__bases__, shifted_class)
    for constructed in _placed_objects(member):
        _initialize_level_shift(node(point, Role.ELEMENT), constructed)


def _placed_objects(category: Category) -> tuple[ObjectOfCategory, ...]:
    """The live objects whose construction inputs name ``category``."""
    return tuple(
        construction_input.canonical_image
        for construction_input in retained_object_inputs()
        if construction_input.identity.category is category
    )


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
