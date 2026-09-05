"""Compile local declarations and selected target classes for the current kernel."""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable, Iterator
from itertools import count
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
    retain_object_by_datum,
    retain_object_input,
    retained_element_input,
    retained_morphism_input,
    retained_object_by_datum,
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
    install_category_object_class,
    install_cat_element_root,
    kernel_base,
    declaration_role,
    record_attribute_writes,
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
    "implement_category",
    "declared_inheritance",
    "declared_subtyping",
    "inheriting_functors",
    "apply_level_shift",
    "install_on_declaration",
    "node",
    "recompile_category",
    "same_node",
]

_LOGGER = logging.getLogger(__name__)


_runtime_ordinals = count()


class SemanticCollisionError(Exception):
    """Two incomparable owners declare one spelling.

    A public method name is one spelling, rejected under POL-CAT-011 and POL-API-011.
    The name of an instance attribute is the other, rejected under POL-API-024, whose
    "the compiler rejects unrelated declarations with the same name" is this refusal in
    the words it uses (``specs/resolution.md``, "Semantic collisions"; D178).
    """


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

    def __init__(
        self, current: Node, targets: tuple[SageCategory, ...], declaration: type[CategoryPoint]
    ) -> None:
        self._current = current
        self._targets = targets
        self._ordinal = next(_runtime_ordinals)
        self.ParentMethods = declaration
        super().__init__()

    @property
    def _cmp_key(self) -> tuple[int, int, int, int]:
        return (0, _ROLE_POSITIONS[self._current.role], self._depth, self._ordinal)

    @lazy_attribute
    def _depth(self) -> int:
        return 1 + max((target._cmp_key[2] for target in self._targets), default=-1)

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
    "_depth",
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
    # Sage CachedRepresentation keys on constructor arguments. A retained category
    # can acquire a new written implementation through Cat.implement.
    runtime = _RuntimeImplementationCategory(
        current, _runtime_targets(current), current.category.local_role_class(current.role)
    )
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


def _is_cat_object_root(current: Node) -> bool:
    """Whether ``current`` is the ``Cat().ObjectType`` node, whose objects are the categories."""
    return current.role is Role.OBJECT and current.category.category() is current.category


def inheriting_functors(category: Category) -> tuple[Functor, ...]:
    """The selected structure functors of ``category`` that carry inheritance, in declared order.

    A functor declared an isofibration carries inheritance from its target; a selected
    functor without that declaration gives access to the structure it selects and
    supplies no implementation.  Order decides precedence among the ones that do, the
    first chosen and coherence assumed (D164 to D167, D37, D159, D165).

    A selected point functor is not one of these edges: it is declared monic and not an
    isofibration, so this reads it out, and what it carries is the categorical level shift
    along the inclusion its image generates (D154, D161, D169; ``refinement.place``).
    """
    from sage_categories.kernel.refinement import traces_inheritance

    return tuple(functor for functor in category.selected_functors() if traces_inheritance(functor))


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
        for category, _ in sorted(_node_runtimes[role].items(), key=lambda item: item[0]._ordinal):
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
    from sage_categories.kernel.roles import declared_roles, category_universal_class

    for provider, role in declared_roles():
        provider_name = _declaration_name(provider)
        relations = result.setdefault(_projection_surface(role), {})
        if provider_name in relations:
            continue
        base = _installed_root_declarations.get(kernel_base(role), category_universal_class().ElementType)
        relations[provider_name] = () if provider is base else (_declaration_name(base),)
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
            if inspect.getattr_static(compiled, name, None) is member:
                continue
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
        object.__setattr__(value, "__class__", role_class)
        return
    declared = type(value)
    with building_role_classes():
        refined = dynamic_class(
            f"{declared.__name__}_with_category",
            (declared, role_class),
            doccls=declared,
            prepend_cls_bases=False,
            cache=True,
        )
    object.__setattr__(value, "__class__", refined)


class _NodeRuntime[Value: CategoryPoint, Datum](NamedTuple):
    initializer: Callable[[Value, Datum], None]
    owner: type[Value]
    written: bool


_node_runtimes: dict[Role, MonoDict] = {role: MonoDict() for role in Role}


def _runtime_node(runtime_class: type[CategoryPoint]) -> Node | None:
    return vars(runtime_class).get("_category_runtime_node")


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


def _stable_role_class(runtime_class: type[CategoryPoint], role: Role) -> type[CategoryPoint]:
    """The kernel role class ``runtime_class`` stands on, which is the role of its values.

    A value's role is the one its compiled class carries, not the role of the node its
    placement is compiled at.  ``Mor(C)(A, B)`` is the full subcategory of ``Mor(C)`` on
    the morphisms ``A -> B``, so its objects are the morphisms of ``C`` and its object
    node reaches ``C.MorphismType`` through that inclusion; a property subcategory of
    ``Mor(C)`` reaches it the same way.  Both are object nodes, and a value of either is a
    morphism (``specs/functor.md``, "The ``Mor(n, C)`` tower": one implementation type,
    one value, two placements).  Reading the class is reading that level identity where
    the structural graph already installed it.
    """
    kernel_roles = tuple(kernel_base(each) for each in Role)
    return next((base for base in runtime_class.__mro__ if base in kernel_roles), kernel_base(role))


def runtime_semantic_bases(
    runtime_class: type[CategoryPoint],
) -> tuple[type[CategoryPoint], ...] | None:
    """Return every semantic and runtime branch of a compiled class in compiler C3 order.

    One declaration can be the one several linearized nodes are compiled from: a
    category class that writes no role class of its own is compiled from the one it
    inherits, and every node under it is compiled from that same declaration.  It is
    read once, at the last node that supplies it, because that is where Sage's
    linearization of those nodes puts it -- a C3 order places a shared base after every
    node that reaches it, and reading it at the first node instead would put it ahead of
    declarations that the nodes between place before it.  Two nodes would then state
    incompatible orders for one pair of declarations, and the projection over them has
    no linearization (D130, ``specs/resolution.md``, "Sage class construction").
    """
    current = _runtime_node(runtime_class)
    if current is None:
        for role, table in _node_runtimes.items():
            for category, runtime in table.items():
                if category.local_role_class(role) is runtime_class:
                    installed = _installed_root_declarations.get(_stable_role_class(runtime.owner, role))
                    if installed is not None and installed is not runtime_class:
                        return (installed,)
        role = declaration_role(runtime_class)
        if role is not None:
            installed = _installed_root_declarations.get(kernel_base(role))
            if installed is not None and installed is not runtime_class:
                return (installed,)
        return None
    supplied = [
        source.category.local_role_class(source.role)
        for source in (current, *_linearized_nodes(current))
    ]
    result: list[type[CategoryPoint]] = [
        declaration
        for position, declaration in enumerate(supplied)
        if not any(declaration is later for later in supplied[position + 1 :])
    ]
    stable_role = _stable_role_class(runtime_class, current.role)
    if not issubclass(stable_role, runtime_class) and not any(
        issubclass(base, stable_role) for base in result
    ):
        result.append(stable_role)
        # A declaration installed on the role root is a semantic base of every value of
        # that role: ``Mor(C).ObjectType`` is installed on the morphism root rather than
        # compiled as a node of its own, and it is where every morphism's shared
        # mathematics is written (D44, D85, D173).
        installed = _installed_root_declarations.get(stable_role)
        if installed is not None and not any(known is installed for known in result):
            result.append(installed)
    return tuple(result)


_installed_root_declarations: dict[type[CategoryPoint], type[CategoryPoint]] = {}


_UNRESOLVED = object()

type _ImageDatum = Callable[[Functor, CategoryPoint], tuple[Node, object]]


class _SelectedAction(NamedTuple):
    """One queued object action out of an owner the kernel has already initialized."""

    functor: Functor
    owner: Node
    target: Node
    datum: object
    representative: CategoryPoint


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


def _unrelated_owners(first: Node, second: Node) -> bool:
    """Whether two reached owners share neither a written declaration nor a class relation.

    This is the relation ``_assert_no_semantic_collisions`` reads for a public method
    spelling, applied to the other spelling a declaration writes: the names of its
    instance state.  Two owners are related when one written declaration supplies both --
    the bimodule of D167 -- or when one's compiled class stands below the other's, which
    is the ordinary refinement an inheriting functor installs.
    """
    if first.category.local_role_class(first.role) is second.category.local_role_class(second.role):
        return False
    first_class, second_class = _runtime(first).owner, _runtime(second).owner
    return not issubclass(first_class, second_class) and not issubclass(second_class, first_class)


def _keep_first_state(
    instance: CategoryPoint,
    installed: dict[str, tuple[object, Node]],
    kernel_state: frozenset[str],
    owner: Node,
    written: set[str],
) -> None:
    """Restore the state an earlier related owner installed over a later owner's write (D37, D56).

    Two reached owners can share one written declaration: a bimodule's two projections
    reach ``Modules(R)`` and ``Modules(S)``, which are two categories of the one written
    ``Modules`` object declaration (D167).  The kernel runs that one initializer for each
    owner, with that owner's own datum (D13), so both write the same attribute names on
    the one instance.  The declared order of the selected structure functors ranks the
    owners and controlled C3 runs them in that order (D56, D165, D166, D167), so the
    first-declared owner's state is the state the value reads, and the local declaration
    ahead of every inherited one keeps its own (``specs/resolution.md``, "Sage class
    construction").  Coherence between the two writes is assumed, so the discarded one is
    the opt-in ``DEBUG`` line D37 gives an unresolved diamond rather than a failure.

    Those rows reach one written declaration reached twice and one owner refined by
    another.  Nothing licenses order to decide between two unrelated owners, and
    ``specs/resolution.md`` ("Semantic collisions") bans using selection order to resolve
    that conflict, so the kernel refuses it loudly instead of answering one owner's
    method with another owner's state (D56).  An attribute name is the second spelling
    that section governs; POL-API-024 owns the refusal (D178).

    ``kernel_state`` holds every name already on the instance when the first owner's turn
    starts, so nothing in it was written by a declaration's initializer and the first-writer
    rule has no owner to name for it.  Two writers put names there.  The kernel roots run
    immediately before and install placement and identity, which are the kernel's own and
    which the declaration that owns them refines from whichever turn it runs on
    (``refinement.place``, D169, D175).  A category value carries, in addition, whatever its
    own class stored: the kernel constructs a category after that written body has run
    (``kernel/roles.py``, ``_install_category_initializer``), so ``_ambient``, ``_name``,
    ``_roots`` and a leaf category's own fields are all present before any turn.  Those are
    the parameters of the one class the value names, not state a reached owner installed.
    """
    for name in written:
        if name in kernel_state:
            continue
        state = vars(instance)[name]
        first = installed.get(name)
        if first is None:
            installed[name] = (state, owner)
            continue
        kept, first_owner = first
        if _unrelated_owners(first_owner, owner):
            raise SemanticCollisionError(
                f"{name!r} is written by both "
                f"{_declaration_name(first_owner.category.local_role_class(first_owner.role))} and "
                f"{_declaration_name(owner.category.local_role_class(owner.role))}, "
                "which are incomparable; name the two mathematical states distinctly"
            )
        if (
            owner.category.local_role_class(owner.role) is not first_owner.category.local_role_class(first_owner.role)
            and issubclass(_runtime(owner).owner, _runtime(first_owner).owner)
        ):
            installed[name] = (state, owner)
            continue
        if state is kept:
            continue
        setattr(instance, name, kept)
        _LOGGER.debug(
            "kept the %s written for %r over the one written for %r on %r",
            name,
            first_owner.category,
            owner.category,
            instance,
        )


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

    An action is run at the turn of the owner it constructs, not at the turn of the owner
    it starts from, so every owner ahead of it in the C3 order is already initialized on
    the instance.  This is what lets the second selected functor's action call the methods
    the instance inherits through the first (D13 as corrected 09-02; ``specs/leaves.md``,
    "An action receives a fully initialized source value").
    """
    # Each reached owner keeps the value that represents ``instance`` in its own category:
    # the instance itself at the root, and the retained image ``F(x)`` below a selected
    # ``F``.  A functor out of an owner runs on that representative, which is a member of
    # its domain; the source value carries the owner's implementation without being one
    # of its objects (POL-MATH-046).
    resolved: list[tuple[Node, object, CategoryPoint]] = [(current, data, instance)]
    queued: list[_SelectedAction] = []
    # Each name written on the instance, held by the owner whose turn wrote it first, so
    # that a later owner's turn cannot displace it (``_keep_first_state``).  Every name
    # already on the instance is exempt: no owner's turn wrote it, so the first-writer rule
    # has no owner to name for it.  Those names are placement and identity, and for a
    # category value also the parameters its own class stored before the kernel constructed
    # it.
    kernel_state = frozenset(vars(instance))
    installed: dict[str, tuple[object, Node]] = {}

    def resolution(owner: Node) -> tuple[object, CategoryPoint] | None:
        return next(((datum, value) for known, datum, value in resolved if same_node(known, owner)), None)

    def run_next_action() -> bool:
        """Run one queued action and record what the owner it reaches is constructed from."""
        while queued:
            action = queued.pop(0)
            if resolution(action.target) is not None:
                continue
            image, built, image_data = image_datum(action.functor, action.representative)
            if image is action.representative:
                # An inclusion is the identity on this value: the target shares the datum
                # this owner was constructed from, and adds nothing to it.
                resolved.append((action.target, action.datum, action.representative))
                return True
            assert same_node(built, action.target) or not _runtime(action.target).written, (
                f"{action.functor!r} out of {type(action.owner.category).__name__} constructs its image at "
                f"{type(built.category).__name__}.{built.role.value}, not at its codomain "
                f"{type(action.target.category).__name__}.{action.target.role.value}, whose declaration initializes local state"
            )
            resolved.append((action.target, image_data, image))
            if not same_node(built, action.target):
                resolved.append((built, image_data, image))
            return True
        return False

    pending = [current]
    ordered: list[Node] = []
    while pending:
        owner = pending.pop()
        if any(same_node(owner, known) for known in ordered):
            continue
        ordered.append(owner)
        pending.extend(reversed([target for _, target in successors(owner)]))
    ordered.extend(owner for owner in context.nodes if not any(same_node(owner, known) for known in ordered))
    for owner in ordered:
        is_point_node = _is_cat_element_root(owner) or (owner.role is Role.ELEMENT and current.role is not Role.ELEMENT)
        while not is_point_node and resolution(owner) is None and run_next_action():
            pass
        found = (None, instance) if is_point_node else resolution(owner)
        assert found is not None, (
            f"no selected functor reaches {owner.category!r}.{owner.role.value} from {current.category!r}"
        )
        datum, representative = found
        runtime = _runtime(owner)
        with record_attribute_writes(instance) as written:
            context.run(owner, lambda runtime=runtime, datum=datum: runtime.initializer(instance, datum))
        _keep_first_state(instance, installed, kernel_state, owner, written)
        if owner.role is not current.role:
            continue
        queued.extend(
            _SelectedAction(functor, owner, target, datum, representative)
            for functor, target in successors(owner)
        )


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
        # ``Cat()`` is an object of ``Cat()``, so it is a point ``* -> Cat()`` and the
        # element declaration belongs in its chain.  This is the level shift
        # ``_role_targets`` performs for every other object role, done by hand because
        # the class this bootstrap allocates is what the first compile is run from.
        provisional_type = dynamic_class(
            f"_{category_type.__name__}Bootstrap",
            (category_type, category_type.ElementType, ObjectOfCategory),
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


def _retention_node(constructing_class: type[CategoryPoint]) -> Node | None:
    """The object node whose values ``constructing_class`` constructs, if it is one's compiled class.

    A category class written over a compiled object class is not one: it constructs a
    category, an object of ``Cat()`` with no datum of its own.
    """
    current = _runtime_node(constructing_class)
    return current if current is not None and current.role is Role.OBJECT else None


def _allocate_object(cls: type[ObjectOfCategory], *arguments: object, **keywords: object) -> ObjectOfCategory:
    """Return the object the constructing category retains for its datum, or a new one (D111).

    A category states its constructors from its datum and keeps no store of its own: one
    object per datum is the kernel's, so the compiled class the constructor names is
    where the retained object is returned instead of a second one being built.  A
    construction with no datum has no key and is retained by nothing; a category class
    written over a compiled object class constructs a category, whose arguments are its
    own parameters and not a datum of ``Cat()``.
    """
    current = _retention_node(cls)
    if current is None:
        return object.__new__(cls)
    data = arguments[0] if arguments else keywords.get("data")
    if data is None:
        return object.__new__(cls)
    retained = retained_object_by_datum(current.category, data)
    return object.__new__(cls) if retained is None else retained


def _initialize_object[Datum](
    instance: ObjectOfCategory,
    data: Datum | None = None,
) -> None:
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        _reject_base_initializer_call(instance)
    if is_constructed(instance):
        # ``_allocate_object`` returned the object this category retains for ``data``,
        # and Python calls the initializer on it again; it is already constructed.
        return
    retention = _retention_node(type(instance))
    current = _construction_node(instance, Role.OBJECT)
    _construct_object_root(current, instance, ObjectRoleIdentity(current.category), data)
    if retention is not None and data is not None:
        retain_object_by_datum(retention.category, data, instance)


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
    domain: ObjectOfCategory | None = None,
    codomain: ObjectOfCategory | None = None,
    data: Datum | None = None,
) -> None:
    active = active_construction_context(instance)
    if active is not None and active.canonical_image is instance:
        _reject_base_initializer_call(instance)
    assert domain is not None and codomain is not None, "a morphism root constructor requires its endpoints"
    current = _construction_node(instance, Role.MORPHISM)
    # A morphism of ``C`` is an object of ``Mor(C)``, and the compiled class the
    # constructor names says which ``C`` it belongs to (``_construction_node``).
    identity = MorphismRoleIdentity(current.category.morphism_category(1), domain, codomain)
    _construct_morphism_root(current, instance, identity, data)


def _debug_unresolved_diamonds(category: Category) -> None:
    """Log each repeated structural target in the owned graph, without resolving it.

    The graph declaration is mathematical input.  A repeated target means two distinct
    structural paths reach one implementation owner.  Controlled C3 still contributes
    that implementation class once; until owned 2-morphism data explicitly records the
    coherence, the only runtime effect is this opt-in diagnostic (D37).
    """
    if not _LOGGER.isEnabledFor(logging.DEBUG):
        return
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
    from sage_categories.kernel.refinement import declares_point, is_placed

    for functor in functors:
        functor_category = category.category().morphism_category(1)
        assert is_placed(functor, functor_category), f"{functor!r} is not an object of {functor_category!r}"
        if declares_point(functor):
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
            _, declared_role = category.role_source(role)
            if declared_role is not role:
                assert role is Role.OBJECT and declared_role is Role.MORPHISM
                normalization_owner = next(
                    owner for owner in type(category).__mro__ if "role_source" in vars(owner)
                )
                root, declaration = kernel_base(current.role), vars(normalization_owner)[Role.OBJECT.value]
                _install_written_body(root, declaration)
                _installed_root_declarations[root] = declaration
            setattr(category, role.value, current.category.role_class(current.role))
            continue
        _install_runtime_node(current)


def _install_runtime_node(current: Node) -> type[CategoryPoint]:
    """Install one compiled node from its private Sage runtime category."""
    compiled = _compiled_class(current)
    compiled._category_runtime_node = current
    _assert_no_semantic_collisions(compiled)
    node_initializer = vars(current.category.local_role_class(current.role)).get("__init__")
    written = node_initializer is not None
    if node_initializer is None:
        node_initializer = _silent_initializer
    assert isinstance(node_initializer, FunctionType)
    if _is_cat_element_root(current):
        install_cat_element_root(compiled)
    if _is_cat_object_root(current):
        install_category_object_class(compiled)
    match current.role:
        case Role.OBJECT:
            compiled.__init__ = _initialize_object
            compiled.__new__ = staticmethod(_allocate_object)
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


def implement_category(category: Category, implementation: type[Category]) -> None:
    """Install a declared implementation on its retained category identity.

    Python's in-place class assignment preserves references to the declaration.
    The ordinary initializer supplies implementation state before roles are compiled.
    """
    object.__setattr__(category, "__class__", implementation)
    implementation.__init__(category)
    category.recompile()


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
            object.__setattr__(constructed, "__class__", _replace_runtime_classes(type(constructed), replacements))
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
