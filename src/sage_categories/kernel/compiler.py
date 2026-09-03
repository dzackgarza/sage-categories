"""Compile local declarations and selected target classes for the current kernel."""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable, Iterator
from types import FunctionType, GenericAlias
from typing import TYPE_CHECKING, Concatenate, Generic, NamedTuple

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
    is_constructed,
    retain_element_input,
    retain_morphism_input,
    retain_object_input,
    retained_element_input,
    retained_morphism_input,
    retained_object_input,
    retained_objects,
)
from sage_categories.kernel.roles import (
    CategoryPoint,
    MorphismOfCategory,
    ObjectOfCategory,
    Role,
    building_role_classes,
    install_category_declaration_root,
    install_cat_element_root,
    kernel_base,
)
from sage_categories.kernel.sage_runtime import MonoDict, SageCategory, dynamic_class, lazy_attribute

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Functor

__all__ = [
    "Node",
    "SemanticCollisionError",
    "compile_category",
    "compiler",
    "construct_category_value",
    "declared_inheritance",
    "declared_subtyping",
    "inheriting_functors",
    "apply_level_shift",
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
    def _cmp_key(self) -> tuple[int, int, int, int]:
        return (0, _ROLE_POSITIONS[self._role], -1, len(self._root.__mro__))

    def super_categories(self) -> list[SageCategory]:
        if self._root is CategoryPoint:
            return []
        base = self._root.__bases__[0]
        return [_cat_element_role_root() if base is CategoryPoint else _role_root(self._role, base)]

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
    def _cmp_key(self) -> tuple[int, int, int, int]:
        role, ordinal = node_key(self._current)
        return (0, role, ordinal, 0)

    def super_categories(self) -> list[SageCategory]:
        return list(self._targets)

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        return self._make_named_class("parent_class", "ParentMethods", cache=True)


class Node(NamedTuple):
    category: Category
    role: Role


_runtime_categories: dict[Role, MonoDict] = {role: MonoDict() for role in Role}

_RUNTIME_CACHE_NAMES = (
    "parent_class",
    "_all_super_categories",
    "_all_super_categories_proper",
    "_set_of_super_categories",
    "_super_categories",
    "_super_categories_for_classes",
)


def _role_root(role: Role, root: type[CategoryPoint]) -> _KernelRoleRootCategory:
    """The Sage-canonical private category ending one role chain at ``root``."""
    return _KernelRoleRootCategory(role, root)


def _kernel_role_root(role: Role) -> _KernelRoleRootCategory:
    """The Sage-canonical private category for one kernel role root."""
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

def node_key(current: Node) -> tuple[int, int]:
    """The position of ``current`` in the total order the C3 merge is controlled by.

    Role order comes first because an object node can acquire a newer element node when
    the category value enters a new placement.  Within one role, construction order
    ranks a category after every structural target it selects.
    """
    return (_ROLE_POSITIONS[current.role], current.category.ordinal())


def node(category: Category, role: Role) -> Node:
    """The normalized node: ``(Mor(C), object)`` is ``(C, morphism)``."""
    if role is Role.OBJECT:
        source, is_morphism = category._object_role_source()
        source_role = Role.MORPHISM if is_morphism else Role.OBJECT
    else:
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
    runtime = _RuntimeImplementationCategory(current, _runtime_targets(current))
    table[current.category] = runtime
    return runtime


def _runtime_targets(current: Node) -> tuple[SageCategory, ...]:
    """The immediate Sage runtime targets of one implementation node."""
    targets: list[SageCategory] = [_runtime_category(target) for _, target in successors(current)]
    if not targets:
        targets.append(_cat_element_role_root() if _is_cat_element_root(current) else _kernel_role_root(current.role))
    if current.role is Role.OBJECT:
        shifted = _runtime_category(node(current.category.category(), Role.ELEMENT))
        if not any(issubclass(target.parent_class, shifted.parent_class) for target in targets):
            targets.append(shifted)
    return tuple(targets)


def _is_cat_element_root(current: Node) -> bool:
    """Whether ``current`` is the preallocated common ``Cat().ElementType`` node."""
    return current.role is Role.ELEMENT and current.category.category() is current.category


def inheriting_functors(category: Category) -> tuple[Functor, ...]:
    """The selected structure functors of ``category`` that carry inheritance, in declared order.

    A functor declared an isofibration carries inheritance from its target; a selected
    functor without that declaration gives access to the structure it selects and
    supplies no implementation.  Order decides precedence among the ones that do, the
    first chosen and coherence assumed (D164 to D167, D37, D159, D165).

    A selected point functor is not one of these edges: it places the category as an
    object of its codomain, and what it carries is the categorical level shift
    (D154, D161, D169; ``refinement.place``).
    """
    from sage_categories.kernel.refinement import traces_inheritance

    return tuple(
        functor
        for functor in category.selected_functors()
        if traces_inheritance(functor) and not functor.codomain().retains_point_functor(functor)
    )


def successors(current: Node) -> tuple[tuple[Functor, Node], ...]:
    """The inheriting functors out of ``current``; each keeps the role it starts in."""
    return tuple(
        (functor, node(functor.codomain(), current.role))
        for functor in inheriting_functors(current.category)
    )


def declared_inheritance(
    category: Category,
    role: Role,
) -> tuple[type[CategoryPoint], ...]:
    """Return one compiled role's semantic declarations in controlled-C3 order.

    The role class is already installed when a category is constructed.  Reading its
    retained C3 relation therefore allocates neither a dynamic class nor a parallel
    linearization; Sage remains the sole owner of C3 (`POL-TYPE-024`,
    `POL-TYPE-025`).
    """
    current = node(category, role)
    declared = runtime_semantic_bases(current.category.role_class(current.role))
    assert declared is not None, (
        f"{current.category!r}.{current.role.value} has no compiled declaration relation"
    )
    return declared


def declared_subtyping(category: Category, role: Role) -> tuple[Category, ...]:
    """Return the distinct direct structure-functor targets for one role.

    This reports category relations exactly as declared by selected functors.  It does
    not infer containment from Python classes, placement, or a public functor image
    (`POL-TYPE-024`, `POL-TYPE-027`).
    """
    current = node(category, role)
    targets: list[Category] = []
    for _, target in successors(current):
        if not any(target.category is known for known in targets):
            targets.append(target.category)
    return tuple(targets)


def _declaration_name(declaration: type[CategoryPoint]) -> str:
    """Return the importable source name of one category-owned declaration."""
    return f"{declaration.__module__}.{declaration.__qualname__}"


class _CompilerProjection:
    """The plugin's read-only view of the compiler's already-installed declarations."""

    def declared_inheritance(self) -> dict[str, dict[str, tuple[str, ...]]]:
        return _inheritance_projection()

    def declared_subtyping(self) -> dict[str, dict[str, tuple[str, ...]]]:
        return _subtyping_projection()


def _projection_surface(role: Role) -> str:
    match role:
        case Role.OBJECT:
            return "object"
        case Role.ELEMENT:
            return "element"
        case Role.MORPHISM:
            return "arrow"


def _projection_providers() -> Iterator[tuple[str, Category, Role, type[CategoryPoint]]]:
    """Yield normalized declaration providers once for every installed role surface."""
    seen: list[Node] = []
    for role in Role:
        for category, _ in _node_runtimes[role].items():
            current = node(category, role)
            if any(same_node(current, known) for known in seen):
                continue
            seen.append(current)
            provider = current.category.local_role_class(current.role)
            yield _projection_surface(role), current.category, current.role, provider


def _inheritance_projection() -> dict[str, dict[str, tuple[str, ...]]]:
    """Project the compiler's C3 declaration order for the static plugin."""
    result: dict[str, dict[str, tuple[str, ...]]] = {}
    for surface_name, category, role, provider in _projection_providers():
        provider_name = _declaration_name(provider)
        names = tuple(
            _declaration_name(declaration)
            for declaration in declared_inheritance(category, role)
        )
        entry = tuple(name for name in names if name != provider_name)
        existing = result.setdefault(surface_name, {}).get(provider_name, ())
        result[surface_name][provider_name] = tuple(
            dict.fromkeys(existing + entry)
        )
    return result


def _subtyping_projection() -> dict[str, dict[str, tuple[str, ...]]]:
    """Project direct selected-functor targets for the static plugin."""
    result: dict[str, dict[str, tuple[str, ...]]] = {}
    for surface_name, category, role, provider in _projection_providers():
        provider_name = _declaration_name(provider)
        names = tuple(
            _declaration_name(node(target, role).category.local_role_class(node(target, role).role))
            for target in declared_subtyping(category, role)
        )
        entry = tuple(name for name in names if name != provider_name)
        existing = result.setdefault(surface_name, {}).get(provider_name, ())
        result[surface_name][provider_name] = tuple(
            dict.fromkeys(existing + entry)
        )
    return result


_COMPILER_PROJECTION = _CompilerProjection()


def compiler() -> _CompilerProjection:
    """Return the declaration reporter consumed by the static projection plugin."""
    return _COMPILER_PROJECTION


def _local_method_names(local_class: type[CategoryPoint]) -> tuple[str, ...]:
    """The public method spellings written on one local declaration."""
    return tuple(
        name
        for name, function in vars(local_class).items()
        if inspect.isfunction(function) and name not in _IGNORED_NAMES and (not name.startswith("_") or name.startswith("__"))
    )


def _install_written_body(compiled: type[CategoryPoint], local: type[CategoryPoint]) -> None:
    """Install each written member of one declaration on the class compiled from it."""
    if Generic in local.__mro__:
        compiled.__class_getitem__ = classmethod(GenericAlias)
    for name, member in vars(local).items():
        if isinstance(member, classmethod | staticmethod | FunctionType):
            setattr(compiled, name, member)


def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: Callable[Concatenate[CategoryPoint, P], R]) -> None:
    """Add one method to a declaration and to the class of every node already compiled from it.

    A compile installs the written body it reads (``_install_written_body``), so a
    declaration extended afterwards must reach the classes that copy is already in.  The
    axiom applications of ``Fun`` are the case: they are compiled when the class stating
    them is created, and the declaration they belong on is ``Cat()``'s morphism role,
    which the bootstrap compiled before that class could exist (POL-CAT-060, D89).

    The nodes are the ones the compiler linearized, which is every node it has built a
    class for.  ``apply_level_shift`` writes onto live role classes the same way.
    """
    setattr(local, name, member)
    for table in _runtime_categories.values():
        for _, runtime in table.items():
            if runtime._current.category.local_role_class(runtime._current.role) is local:
                compiled = runtime.parent_class
                setattr(compiled, name, member)


def _compiled_class(current: Node) -> type[CategoryPoint]:
    """The Sage-compiled implementation class of ``current``'s private runtime category."""
    with building_role_classes():
        compiled = _runtime_category(current).parent_class
    _install_written_body(compiled, current.category.local_role_class(current.role))
    return compiled


def _assert_no_semantic_collisions(*surfaces: type[CategoryPoint]) -> None:
    """Reject one public spelling from incomparable owners in Sage's compiled MROs.

    The owner of a spelling is the written declaration that supplies it.  One
    declaration compiled at two incomparable nodes -- the opposite-category role
    written once and compiled for each ``C.op()`` -- is one mathematical operation,
    not a collision.
    """
    runtime_by_class = {
        runtime.__dict__["parent_class"]: runtime
        for table in _runtime_categories.values()
        for _, runtime in table.items()
        if "parent_class" in runtime.__dict__
    }
    owners: dict[str, tuple[Node, type[CategoryPoint], type[CategoryPoint]]] = {}
    for surface in surfaces:
        for implementation in surface.__mro__:
            runtime = runtime_by_class.get(implementation)
            if runtime is None:
                continue
            declaration = runtime._current.category.local_role_class(runtime._current.role)
            for name in _local_method_names(runtime.ParentMethods):
                previous = owners.get(name)
                if previous is None:
                    owners[name] = (runtime._current, implementation, declaration)
                    continue
                previous_node, previous_class, previous_declaration = previous
                if declaration is previous_declaration:
                    continue
                if issubclass(implementation, previous_class) or issubclass(previous_class, implementation):
                    continue
                raise SemanticCollisionError(
                    f"{name!r} is declared by both {previous_node.category!r} and {runtime._current.category!r}, "
                    "which are incomparable; name the two mathematical operations distinctly"
                )


def _refine_implementation_class(value: CategoryPoint, role_class: type[CategoryPoint]) -> None:
    """Refine one owned value with a compiled implementation class."""
    if issubclass(type(value), role_class):
        return
    if issubclass(role_class, type(value)):
        value.__class__ = role_class
        return
    declared = type(value)
    with building_role_classes():
        value.__class__ = dynamic_class(
            f"{declared.__name__}_with_category",
            (declared, role_class),
            doccls=declared,
            prepend_cls_bases=False,
            cache=True,
        )


class _NodeRuntime[Value: CategoryPoint, Datum](NamedTuple):
    initializer: Callable[[Value, Datum], None]
    owner: type[Value]
    written: bool


_node_runtimes: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


def _runtime_node(runtime_class: type[CategoryPoint]) -> Node | None:
    for role, table in _node_runtimes.items():
        for category, runtime in table.items():
            if runtime.owner is runtime_class:
                return Node(category, role)
    return None


def runtime_declaration(runtime_class: type[CategoryPoint]) -> type[CategoryPoint] | None:
    """Return the semantic declaration copied into one compiled role class."""
    current = _runtime_node(runtime_class)
    return None if current is None else current.category.local_role_class(current.role)


def runtime_implementation_class(declaration: type[CategoryPoint]) -> type[CategoryPoint]:
    """Return the compiled runtime class for a local semantic declaration, if installed."""
    for table in _node_runtimes.values():
        for _, runtime in table.items():
            if runtime_declaration(runtime.owner) is declaration:
                return runtime.owner
    return declaration


def _runtime[Value: CategoryPoint, Datum](current: Node) -> _NodeRuntime[Value, Datum]:
    table = _node_runtimes[current.role]
    assert current.category in table, f"the {current.role.value} runtime of {current.category!r} is not compiled"
    return table[current.category]


def _silent_initializer[Value: CategoryPoint, Datum](_instance: Value, _datum: Datum) -> None:
    """The initializer of a declaration with no local ``__init__``: it adds no state."""



def _linearized_nodes(current: Node) -> tuple[Node, ...]:
    """The selected target nodes in the private Sage category's C3 order, after ``current`` itself."""
    return tuple(
        runtime._current
        for runtime in _runtime_category(current)._all_super_categories
        if isinstance(runtime, _RuntimeImplementationCategory) and not same_node(runtime._current, current)
    )


def runtime_semantic_bases(
    runtime_class: type[CategoryPoint],
) -> tuple[type[CategoryPoint], ...] | None:
    """Return every semantic and runtime branch of a compiled class in compiler C3 order."""
    current = _runtime_node(runtime_class)
    if current is None:
        return None
    declaration = current.category.local_role_class(current.role)
    result: list[type[CategoryPoint]] = [declaration]
    for source in _linearized_nodes(current):
        source_declaration = source.category.local_role_class(source.role)
        if not any(source_declaration is known for known in result):
            result.append(source_declaration)
    stable_role = kernel_base(current.role)
    if not issubclass(stable_role, runtime_class) and not any(
        issubclass(base, stable_role) for base in result
    ):
        result.append(stable_role)
    return tuple(result)


_UNRESOLVED = object()

type _ImageDatum = Callable[[Functor, CategoryPoint], tuple[Node, object]]


def _initialize_kernel_roots(instance: CategoryPoint, role: Role) -> None:
    """Install placement and identity from the active construction context, before any declaration runs."""
    if role is not Role.ELEMENT:
        instance._initialize_placement()
    instance._initialize_identity()


def _with_cat_element_node(nodes: tuple[Node, ...], universe: Category) -> tuple[Node, ...]:
    """Append the common ``Cat().ElementType`` root node when the linearization lacks it.

    An object of ``C`` and a morphism of ``C`` (an object of ``Mor(C)``) are each a point
    ``* -> K`` of their category (``specs/functor.md``, "Compiled implementation classes").
    """
    target = node(universe, Role.ELEMENT)
    if any(same_node(owner, target) for owner in nodes):
        return nodes
    return (*nodes, target)


def _initialize_graph(
    context: ObjectConstructionContext | ElementConstructionContext | MorphismConstructionContext,
    current: Node,
    instance: CategoryPoint,
    data: object,
    image_datum: _ImageDatum,
) -> None:
    """Run every reached local initializer once, each with its owner's datum (D13).

    The root runs with the constructor's datum.  A selected target runs with the datum
    its structure functor feeds to the target constructor: the kernel runs the ordinary
    action on the value under construction and reads the datum its image was
    constructed from.  A point node of the category runs with none.  The first
    structural path to reach an owner supplies its datum (D56).  No declaration calls a
    base-class initializer.
    """
    # Each reached owner keeps the value that represents ``instance`` in its own category:
    # the instance itself at the root, and the retained image ``F(x)`` below a selected
    # ``F``.  A functor out of an owner runs on that representative, which is a member of
    # its domain; the source value carries the owner's implementation without being one
    # of its objects (POL-MATH-046).
    resolved: list[tuple[Node, object, CategoryPoint]] = [(current, data, instance)]

    def resolution(owner: Node) -> tuple[object, CategoryPoint] | None:
        return next(((datum, value) for known, datum, value in resolved if same_node(known, owner)), None)

    for owner in context.nodes:
        is_point_node = _is_cat_element_root(owner) or (owner.role is Role.ELEMENT and current.role is not Role.ELEMENT)
        found = (None, instance) if is_point_node else resolution(owner)
        assert found is not None, (
            f"no selected functor reaches {owner.category!r}.{owner.role.value} from {current.category!r}"
        )
        datum, representative = found
        runtime = _runtime(owner)
        context.run(owner, lambda runtime=runtime, datum=datum: runtime.initializer(instance, datum))
        if owner.role is not current.role:
            continue
        for functor, target in successors(owner):
            if resolution(target) is not None:
                continue
            image, built, image_data = image_datum(functor, representative)
            if image is representative:
                # An inclusion is the identity on this value: the target shares the datum
                # this owner was constructed from, and adds nothing to it.
                resolved.append((target, datum, representative))
                continue
            assert same_node(built, target) or not _runtime(target).written, (
                f"{functor!r} out of {type(owner.category).__name__} constructs its image at "
                f"{type(built.category).__name__}.{built.role.value}, not at its codomain "
                f"{type(target.category).__name__}.{target.role.value}, whose declaration initializes local state"
            )
            resolved.append((target, image_data, image))
            if not same_node(built, target):
                resolved.append((built, image_data, image))


def _object_image_datum(functor: Functor, instance: CategoryPoint) -> tuple[CategoryPoint, Node, object]:
    image = functor.on_object(instance)
    if image is instance:
        return image, Node(functor.codomain(), Role.OBJECT), None
    retained = retained_object_input(image)
    return image, node(retained.identity.category, Role.OBJECT), retained.datum


def _morphism_image_datum(functor: Functor, instance: CategoryPoint) -> tuple[CategoryPoint, Node, object]:
    image = functor.on_morphism(instance)
    if image is instance:
        return image, Node(functor.codomain(), Role.MORPHISM), None
    retained = retained_morphism_input(image)
    return image, node(retained.identity.category, Role.OBJECT), retained.datum


def _element_image_datum(functor: Functor, instance: CategoryPoint) -> tuple[CategoryPoint, Node, object]:
    """The image of a point ``t: T -> X`` is the element of ``F(X)`` defined by ``F(t)`` (D17)."""
    defining_morphism = instance.defining_morphism()
    image_morphism = functor.on_morphism(defining_morphism)
    if image_morphism is defining_morphism:
        # An inclusion fixes the defining morphism, so it fixes the element it defines;
        # that element is the one under construction and is not yet retained.
        return instance, Node(functor.codomain(), Role.ELEMENT), None
    image = functor.codomain().element_from_defining_morphism(image_morphism)
    return image, _construction_node(image, Role.ELEMENT), retained_element_input(image).datum


def _construct_object_root[Datum](
    current: Node,
    instance: ObjectOfCategory,
    identity: ObjectRoleIdentity,
    data: Datum,
) -> None:
    root = ObjectConstructionInput(instance, identity, data)
    retain_object_input(root)
    cat_element_identity = CategoryPointIdentity(identity.category)
    nodes = (current, *_linearized_nodes(current))
    assert all(owner.role is not Role.MORPHISM for owner in nodes), (
        f"the object graph of {current.category!r} reaches a morphism implementation"
    )
    context = ObjectConstructionContext(instance, identity, cat_element_identity, nodes)
    token = activate_object_context(context)
    try:
        _initialize_kernel_roots(instance, Role.OBJECT)
        _initialize_graph(context, current, instance, data, _object_image_datum)
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
    nodes = _with_cat_element_node(
        (current, *_linearized_nodes(current)),
        identity.defining_morphism.base_category().universe(),
    )
    context = ElementConstructionContext(instance, identity, identity, nodes)
    token = activate_element_context(context)
    try:
        _initialize_kernel_roots(instance, Role.ELEMENT)
        _initialize_graph(context, current, instance, data, _element_image_datum)
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
    nodes = _with_cat_element_node((current, *_linearized_nodes(current)), identity.category.universe())
    context = MorphismConstructionContext(instance, identity, cat_element_identity, nodes)
    token = activate_morphism_context(context)
    try:
        _initialize_kernel_roots(instance, Role.MORPHISM)
        _initialize_graph(context, current, instance, data, _morphism_image_datum)
        context.assert_complete()
    finally:
        deactivate_morphism_context(token)


def construct_category_singleton[Value: ObjectOfCategory](category_type: type[Value]) -> Value:
    """Allocate ``Cat()`` and start its provisional constructor chain inside its object context."""
    install_category_declaration_root(category_type.ObjectType, category_type)
    with building_role_classes():
        provisional_type = dynamic_class(
            f"_{category_type.__name__}Bootstrap",
            (category_type, ObjectOfCategory),
            doccls=category_type,
            prepend_cls_bases=False,
            cache=True,
        )
    instance = provisional_type.__new__(provisional_type)
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
        _initialize_kernel_roots(instance, Role.OBJECT)
        provisional_type.__init__(instance)
        context.assert_complete()
    finally:
        deactivate_object_context(token)
    return instance


def construct_category_value(instance: ObjectOfCategory) -> None:
    """Construct a category that wrote its own initializer to store its parameters.

    A category is an object of ``Cat()``, so a category class with no initializer is
    constructed by the compiled object initializer it inherits.  A class that stores
    parameters shadows that initializer with its own; the kernel runs the construction
    it shadowed, after the written body and with no base call from the class (D13, D110,
    ``POL-LEAF-063``).

    A class in ``Cat`` whose written initializer reaches the compiled one through its
    own chain is constructed by that call, and the bootstrap runs the written body of
    ``Cat()`` itself inside its construction context.  Both are already constructed
    when the written body returns, and the kernel adds nothing to them here.
    """
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        return
    if is_constructed(instance):
        return
    _initialize_object(instance)


def _construction_node(instance: CategoryPoint, role: Role) -> Node:
    """The compiled node whose direct role class constructed ``instance``."""
    by_class = {runtime.owner: Node(category, role) for category, runtime in _node_runtimes[role].items()}
    current = next((by_class[base] for base in type(instance).__mro__ if base in by_class), None)
    assert current is not None, f"{type(instance)!r} has no compiled {role.value} class"
    return current


def _reject_base_initializer_call(instance: CategoryPoint) -> None:
    """A compiled initializer re-entered on the value under construction: a declaration called a base initializer."""
    raise AssertionError(
        f"a declaration of {type(instance).__name__} called a base-class initializer during construction; "
        "the kernel runs every reached initializer itself (D13)"
    )


def _initialize_object[Datum](
    instance: ObjectOfCategory,
    category: Category | None = None,
    data: Datum | None = None,
) -> None:
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        _reject_base_initializer_call(instance)
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
        _reject_base_initializer_call(instance)
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
        _reject_base_initializer_call(instance)
    assert category is not None and domain is not None and codomain is not None, (
        "a morphism root constructor requires its category and endpoints"
    )
    current = _construction_node(instance, Role.MORPHISM)
    _construct_morphism_root(current, instance, MorphismRoleIdentity(category, domain, codomain), data)


_LOGGER = logging.getLogger(__name__)


def _debug_unresolved_diamonds(category: Category) -> None:
    """Log each repeated structural target in the owned graph, without resolving it.

    The graph declaration is mathematical input.  A repeated target means two distinct
    structural paths reach one implementation owner.  Controlled C3 still contributes
    that implementation class once; until owned 2-morphism data explicitly records the
    coherence, the only runtime effect is this opt-in diagnostic (D37).
    """
    paths: MonoDict = MonoDict()

    def walk(source: Category, path: tuple[Category, ...]) -> None:
        for functor in inheriting_functors(source):
            target = functor.codomain()
            next_path = (*path, target)
            if target not in paths:
                paths[target] = []
            paths[target].append(next_path)
            assert not any(target is ancestor for ancestor in path), (
                f"the structural graph contains a cycle through {target!r}"
            )
            walk(target, next_path)

    walk(category, (category,))
    for target, target_paths in paths.items():
        if len(target_paths) < 2:
            continue
        rendered = " ; ".join(" -> ".join(repr(node) for node in path) for path in target_paths)
        _LOGGER.debug(
            "unresolved structural diamond to %r from %r: %s",
            target,
            category,
            rendered,
        )


def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile the three role classes of ``category`` from its local declarations and its selected functors."""
    from sage_categories.kernel.refinement import is_placed

    for functor in functors:
        functor_category = category.category().morphism_category(1)
        assert is_placed(functor, functor_category), f"{functor!r} is not an object of {functor_category!r}"
        if functor.codomain().retains_point_functor(functor):
            # A selected point functor is the arrow ``* -> D`` that places this category
            # as an object of ``D``; it starts at the terminal category, not here, and
            # what it carries is the level shift rather than an implementation edge
            # (D154, D161, D169; ``refinement.place``).
            continue
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
    _debug_unresolved_diamonds(category)
    for role in _COMPILE_ORDER:
        current = node(category, role)
        if current.category is not category:
            if current.role is role:
                setattr(category, role.value, current.category.role_class(current.role))
                continue
            assert role is Role.OBJECT and current.role is Role.MORPHISM
            normalization_owner = next(
                owner for owner in type(category).__mro__ if "_object_role_source" in vars(owner)
            )
            _install_written_body(
                kernel_base(current.role),
                vars(normalization_owner)[Role.OBJECT.value],
            )
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        _install_runtime_node(current)


def _install_runtime_node(current: Node) -> type[CategoryPoint]:
    """Install one compiled node from its private Sage runtime category."""
    compiled = _compiled_class(current)
    _assert_no_semantic_collisions(compiled)
    node_initializer = vars(compiled).get("__init__")
    written = node_initializer is not None
    if node_initializer is None:
        node_initializer = _silent_initializer
    assert isinstance(node_initializer, FunctionType)
    if _is_cat_element_root(current):
        install_cat_element_root(compiled)
    match current.role:
        case Role.OBJECT:
            compiled.__init__ = _initialize_object
        case Role.ELEMENT:
            compiled.__init__ = _initialize_element
        case Role.MORPHISM:
            compiled.__init__ = _initialize_morphism
    _node_runtimes[current.role][current.category] = _NodeRuntime(node_initializer, compiled, written)
    setattr(current.category, current.role.value, compiled)
    return compiled


def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    """Compile ``category`` again after an implementation claims its declaration (D80)."""
    for role in Role:
        table = _runtime_categories[role]
        if category in table:
            del table[category]
        runtimes = tuple(runtime for _, runtime in table.items())
        for runtime in runtimes:
            for name in _RUNTIME_CACHE_NAMES:
                runtime.__dict__.pop(name, None)
    compile_category(category, functors)


def apply_level_shift(member: Category, placement: Category) -> None:
    """Rebuild the object implementation graph after a category placement changes."""
    current = node(member, Role.OBJECT)
    changed = _runtime_category(current)
    shifted = _runtime_category(node(placement, Role.ELEMENT))
    if issubclass(changed.parent_class, shifted.parent_class):
        return
    affected = tuple(
        runtime
        for table in _runtime_categories.values()
        for _, runtime in table.items()
        if runtime is changed or any(parent is changed for parent in runtime._all_super_categories)
    )
    old_classes = {runtime.parent_class: runtime for runtime in affected}
    old_nodes = {
        runtime: _linearized_nodes(runtime._current)
        for runtime in affected
    }
    changed._targets = _runtime_targets(current)
    for runtime in affected:
        for name in _RUNTIME_CACHE_NAMES:
            runtime.__dict__.pop(name, None)
    replacements = {
        old_class: _install_runtime_node(runtime._current)
        for old_class, runtime in old_classes.items()
    }
    for runtime in affected:
        if runtime._current.role is not Role.OBJECT:
            continue
        added = tuple(
            reached
            for reached in _linearized_nodes(runtime._current)
            if not any(same_node(reached, old) for old in old_nodes[runtime])
        )
        for constructed in _placed_objects(runtime._current.category):
            constructed.__class__ = _replace_runtime_classes(type(constructed), replacements)
            _initialize_added_object_nodes(constructed, added)


def _replace_runtime_classes(
    candidate: type[CategoryPoint],
    replacements: dict[type[CategoryPoint], type[CategoryPoint]],
) -> type[CategoryPoint]:
    """Rebuild a dynamic value class over replacement runtime classes."""
    if candidate in replacements:
        return replacements[candidate]
    bases = tuple(_replace_runtime_classes(base, replacements) for base in candidate.__bases__)
    if bases == candidate.__bases__:
        return candidate
    with building_role_classes():
        return dynamic_class(
            candidate.__name__,
            bases,
            doccls=candidate,
            prepend_cls_bases=False,
            cache=True,
        )


def _initialize_added_object_nodes(value: ObjectOfCategory, added: tuple[Node, ...]) -> None:
    """Initialize the new nodes of one rebuilt object implementation graph."""
    if not added:
        return
    assert all(current.role is Role.ELEMENT for current in added), (
        f"a placement of {value!r} added a non-point node: {added!r}"
    )
    root = retained_object_input(value)
    context = ObjectConstructionContext(value, root.identity, CategoryPointIdentity(root.identity.category), added)
    token = activate_object_context(context)
    try:
        for current in added:
            runtime = _runtime(current)
            context.run(current, lambda runtime=runtime: runtime.initializer(value, None))
        context.assert_complete()
    finally:
        deactivate_object_context(token)


def _placed_objects(category: Category) -> tuple[ObjectOfCategory, ...]:
    """The live objects whose construction inputs name ``category``."""
    return retained_objects(category)
