"""Define the private initialization records used by the current compiler."""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role, role_of
from sage_categories.kernel.sage_runtime import MonoDict

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.kernel.compiler import Node


type ObjectRealization = Callable[[ObjectOfCategory, type[ObjectOfCategory]], None]
_object_realization: ObjectRealization | None = None


def install_object_realization(realization: ObjectRealization) -> None:
    """Install the interpretation of a category structure on a retained object."""
    global _object_realization
    _object_realization = realization


def realize_object(value: ObjectOfCategory, category_type: type[ObjectOfCategory]) -> None:
    """Give the retained object the supplied mathematical category structure."""
    assert _object_realization is not None
    _object_realization(value, category_type)

__all__ = [
    "CatElementRoleIdentity",
    "CategoryPointIdentity",
    "ElementConstructionContext",
    "ElementConstructionInput",
    "ElementRoleIdentity",
    "MorphismConstructionContext",
    "MorphismConstructionInput",
    "MorphismRoleIdentity",
    "ObjectConstructionContext",
    "ObjectConstructionInput",
    "ObjectRoleIdentity",
    "activate_element_context",
    "activate_morphism_context",
    "activate_object_context",
    "active_construction_context",
    "active_element_context",
    "active_morphism_context",
    "active_object_context",
    "deactivate_element_context",
    "deactivate_morphism_context",
    "deactivate_object_context",
    "is_constructed",
    "retain_element_input",
    "retain_morphism_input",
    "retain_object_input",
    "retain_object_by_datum",
    "retained_element_input",
    "retained_input",
    "retained_morphism_input",
    "retained_object_by_datum",
    "retained_object_input",
    "retained_objects",
]


@dataclass(slots=True, eq=False)
class ObjectRoleIdentity:
    """The kernel identity of an object in one category."""

    category: Category
    universe: Category | None = None


@dataclass(frozen=True, slots=True, eq=False)
class ElementRoleIdentity:
    """A point ``1_C -> X`` of an object, retained by its defining morphism (D16)."""

    defining_morphism: MorphismOfCategory


@dataclass(frozen=True, slots=True, eq=False)
class CategoryPointIdentity:
    """A point ``* -> C``: an object of ``C``, or a morphism of ``C`` as an object of ``Mor(C)``."""

    parent: Category


type CatElementRoleIdentity = ElementRoleIdentity | CategoryPointIdentity


@dataclass(frozen=True, slots=True, eq=False)
class MorphismRoleIdentity:
    """The kernel identity of a morphism in one placement."""

    category: Category
    domain: ObjectOfCategory
    codomain: ObjectOfCategory


@dataclass(frozen=True, slots=True, eq=False)
class ObjectConstructionInput[Value: ObjectOfCategory, Datum]:
    """The canonical object, its kernel identity, and one node's local datum."""

    canonical_image: Value
    identity: ObjectRoleIdentity
    datum: Datum


@dataclass(frozen=True, slots=True, eq=False)
class ElementConstructionInput[Value: CategoryPoint, Datum]:
    """The canonical generalized element, its identity, and one local datum."""

    canonical_image: Value
    identity: CatElementRoleIdentity
    datum: Datum


@dataclass(frozen=True, slots=True, eq=False)
class MorphismConstructionInput[Value: MorphismOfCategory, Datum]:
    """The canonical morphism, its kernel identity, and one local datum."""

    canonical_image: Value
    identity: MorphismRoleIdentity
    datum: Datum


# Identity-keyed storage is necessary because mathematical equality can be
# proposition-valued.  The retained input is the input of the value's own root node.
_object_inputs: MonoDict = MonoDict()
_element_inputs: MonoDict = MonoDict()
_morphism_inputs: MonoDict = MonoDict()



def retain_object_input[Value: ObjectOfCategory, Datum](construction_input: ObjectConstructionInput[Value, Datum]) -> None:
    value = construction_input.canonical_image
    if value in _object_inputs:
        assert _object_inputs[value] is construction_input, f"{value!r} already retains a different object construction input"
        return
    _object_inputs[value] = construction_input


def retain_element_input[Value: CategoryPoint, Datum](construction_input: ElementConstructionInput[Value, Datum]) -> None:
    value = construction_input.canonical_image
    if value in _element_inputs:
        assert _element_inputs[value] is construction_input, f"{value!r} already retains a different element construction input"
        return
    _element_inputs[value] = construction_input


def retain_morphism_input[Value: MorphismOfCategory, Datum](construction_input: MorphismConstructionInput[Value, Datum]) -> None:
    value = construction_input.canonical_image
    if value in _morphism_inputs:
        assert _morphism_inputs[value] is construction_input, f"{value!r} already retains a different morphism construction input"
        return
    _morphism_inputs[value] = construction_input


def retained_objects(category: Category) -> tuple[ObjectOfCategory, ...]:
    """The live objects whose retained construction input names ``category``."""
    return tuple(
        construction_input.canonical_image
        for _, construction_input in _object_inputs.items()
        if construction_input.identity.category is category
    )


def is_constructed(value: ObjectOfCategory) -> bool:
    """Whether the kernel already constructed ``value`` as an object."""
    return value in _object_inputs


def retained_object_input[Value: ObjectOfCategory, Datum](value: Value) -> ObjectConstructionInput[Value, Datum]:
    assert value in _object_inputs, f"{value!r} retains no object construction input"
    return _object_inputs[value]


def retain_category_universe(value: ObjectOfCategory, universe: Category) -> None:
    """Retain the universe in which this object's category structure was constructed."""
    identity = retained_object_input(value).identity
    assert identity.universe is None or identity.universe is universe
    identity.universe = universe


def retained_element_input[Value: CategoryPoint, Datum](value: Value) -> ElementConstructionInput[Value, Datum]:
    assert value in _element_inputs, f"{value!r} retains no element construction input"
    return _element_inputs[value]


def retained_morphism_input[Value: MorphismOfCategory, Datum](value: Value) -> MorphismConstructionInput[Value, Datum]:
    assert value in _morphism_inputs, f"{value!r} retains no morphism construction input"
    return _morphism_inputs[value]


# One object per datum, for each category that constructs objects from a datum.  The
# outer key is the constructing category, by identity.  The inner key is the datum, and
# D111 assigns the table by its equality: an owned datum has proposition-valued equality
# and is keyed by identity in a Sage ``MonoDict``; any other datum is an ordinary exact
# key and is kept in a dict, which is the equality that datum itself defines.
_objects_by_owned_datum: MonoDict = MonoDict()
_objects_by_datum: MonoDict = MonoDict()


def _objects_by[Datum](category: Category, datum: Datum) -> MonoDict | dict[Datum, ObjectOfCategory]:
    """The table ``category`` retains its objects in for a datum of this equality (D111)."""
    tables, empty = (
        (_objects_by_owned_datum, MonoDict) if isinstance(datum, CategoryPoint) else (_objects_by_datum, dict)
    )
    if category not in tables:
        tables[category] = empty()
    return tables[category]


def retained_object_by_datum[Datum](category: Category, datum: Datum) -> ObjectOfCategory | None:
    """The object ``category`` retains for ``datum``, or ``None`` if it retains none yet."""
    table = _objects_by(category, datum)
    return table[datum] if datum in table else None


def retain_object_by_datum[Value: ObjectOfCategory, Datum](category: Category, datum: Datum, value: Value) -> None:
    """Retain ``value`` as the object ``category`` constructs from ``datum``."""
    table = _objects_by(category, datum)
    assert datum not in table, f"{category!r} already retains an object for {datum!r}"
    table[datum] = value


def retained_input[Value: CategoryPoint, Datum](
    value: Value,
) -> ObjectConstructionInput[Value, Datum] | ElementConstructionInput[Value, Datum] | MorphismConstructionInput[Value, Datum]:
    """The root input ``value`` retains, in the role it was constructed in.

    The node ``(Mor(C), object)`` *is* the node ``(C, morphism)`` (POL-CAT-021), so the
    objects of a morphism category are morphisms and retain a morphism input.  A caller
    that names a value rather than a node asks for it this way: the role of the value
    selects the table, never the role of the node that asked.
    """
    match role_of(value):
        case Role.OBJECT:
            assert isinstance(value, ObjectOfCategory)
            return retained_object_input(value)
        case Role.MORPHISM:
            assert isinstance(value, MorphismOfCategory)
            return retained_morphism_input(value)
        case Role.ELEMENT:
            return retained_element_input(value)
    raise AssertionError(f"{value!r} is not an owned value")


@dataclass(slots=True)
class ObjectConstructionContext:
    """One object identity and the closed node steps of its C3 constructor chain."""

    canonical_image: ObjectOfCategory
    identity: ObjectRoleIdentity
    cat_element_identity: CategoryPointIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)
    initializing_image: ObjectOfCategory | None = None

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        assert not any(owner.category is node.category and owner.role is node.role for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        assert any(owner.category is node.category and owner.role is node.role for owner in self.nodes), (
            f"{node.category!r}.{node.role.value} is not a node of this constructor chain"
        )
        self.initialized.append(node)
        initialize()

    def assert_complete(self) -> None:
        missing = [
            owner
            for owner in self.nodes
            if not any(done.category is owner.category and done.role is owner.role for done in self.initialized)
        ]
        assert not missing, f"the constructor chain did not initialize {missing[0].category!r}.{missing[0].role.value}"


@dataclass(slots=True)
class ElementConstructionContext:
    """One element identity and the closed node steps of its C3 constructor chain."""

    canonical_image: CategoryPoint
    identity: ElementRoleIdentity
    cat_element_identity: ElementRoleIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        assert not any(owner.category is node.category and owner.role is node.role for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        assert any(owner.category is node.category and owner.role is node.role for owner in self.nodes), (
            f"{node.category!r}.{node.role.value} is not a node of this constructor chain"
        )
        self.initialized.append(node)
        initialize()

    def assert_complete(self) -> None:
        missing = [
            owner
            for owner in self.nodes
            if not any(done.category is owner.category and done.role is owner.role for done in self.initialized)
        ]
        assert not missing, f"the constructor chain did not initialize {missing[0].category!r}.{missing[0].role.value}"


@dataclass(slots=True)
class MorphismConstructionContext:
    """One morphism identity and the closed node steps of its C3 constructor chain."""

    canonical_image: MorphismOfCategory
    identity: MorphismRoleIdentity
    cat_element_identity: CategoryPointIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        assert not any(owner.category is node.category and owner.role is node.role for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        assert any(owner.category is node.category and owner.role is node.role for owner in self.nodes), (
            f"{node.category!r}.{node.role.value} is not a node of this constructor chain"
        )
        self.initialized.append(node)
        initialize()

    def assert_complete(self) -> None:
        missing = [
            owner
            for owner in self.nodes
            if not any(done.category is owner.category and done.role is owner.role for done in self.initialized)
        ]
        assert not missing, f"the constructor chain did not initialize {missing[0].category!r}.{missing[0].role.value}"


_object_context: ContextVar[ObjectConstructionContext | None] = ContextVar("object construction context", default=None)
_element_context: ContextVar[ElementConstructionContext | None] = ContextVar("element construction context", default=None)
_morphism_context: ContextVar[MorphismConstructionContext | None] = ContextVar("morphism construction context", default=None)


def active_object_context() -> ObjectConstructionContext | None:
    return _object_context.get()


def active_element_context() -> ElementConstructionContext | None:
    return _element_context.get()


def active_morphism_context() -> MorphismConstructionContext | None:
    return _morphism_context.get()


def active_construction_context(
    value: CategoryPoint,
) -> ObjectConstructionContext | ElementConstructionContext | MorphismConstructionContext | None:
    """The active role-construction context for ``value``."""
    contexts = tuple(
        context
        for context in (active_object_context(), active_element_context(), active_morphism_context())
        if context is not None and context.canonical_image is value
    )
    assert len(contexts) <= 1, f"{value!r} cannot have two active construction contexts"
    return contexts[0] if contexts else None


def activate_object_context(context: ObjectConstructionContext) -> Token[ObjectConstructionContext | None]:
    return _object_context.set(context)


def activate_element_context(context: ElementConstructionContext) -> Token[ElementConstructionContext | None]:
    return _element_context.set(context)


def activate_morphism_context(context: MorphismConstructionContext) -> Token[MorphismConstructionContext | None]:
    return _morphism_context.set(context)


def deactivate_object_context(token: Token[ObjectConstructionContext | None]) -> None:
    _object_context.reset(token)


def deactivate_element_context(token: Token[ElementConstructionContext | None]) -> None:
    _element_context.reset(token)


def deactivate_morphism_context(token: Token[MorphismConstructionContext | None]) -> None:
    _morphism_context.reset(token)
