"""State-bearing role construction (POL-KERNEL-029, POL-FUN-035).

Each public value retains one root input.  The input keeps the role identity,
the local typed datum, and the canonical public value as separate fields.
During initialization, one role-specific context holds one zero-argument step
per node.  Each step closes over its exact typed input before the C3 chain starts.
"""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict

from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory, Role, role_of

if TYPE_CHECKING:
    from sage_categories.cat.category import Category
    from sage_categories.kernel.compiler import Node

__all__ = [
    "ArrowStageIdentity",
    "CatElementRoleIdentity",
    "ElementConstructionContext",
    "ElementConstructionInput",
    "ElementRoleIdentity",
    "GeneralCategoryPointIdentity",
    "MorphismConstructionContext",
    "MorphismConstructionInput",
    "MorphismRoleIdentity",
    "ObjectConstructionContext",
    "ObjectConstructionInput",
    "ObjectRoleIdentity",
    "ObjectStageIdentity",
    "activate_element_context",
    "activate_morphism_context",
    "activate_object_context",
    "active_element_context",
    "active_construction_context",
    "active_morphism_context",
    "active_object_context",
    "deactivate_element_context",
    "deactivate_morphism_context",
    "deactivate_object_context",
    "retain_element_input",
    "retain_morphism_input",
    "retain_object_input",
    "retained_element_input",
    "retained_input",
    "retained_morphism_input",
    "retained_object_input",
]


def _same_node(first: Node, second: Node) -> bool:
    return first.category is second.category and first.role is second.role


@dataclass(frozen=True, slots=True, eq=False)
class ObjectRoleIdentity:
    """The kernel identity of an object in one category."""

    category: Category


@dataclass(frozen=True, slots=True, eq=False)
class GeneralCategoryPointIdentity:
    """A generalized element given by its defining morphism."""

    defining_morphism: MorphismOfCategory


# The ordinary element constructor keeps this public name.
ElementRoleIdentity = GeneralCategoryPointIdentity


@dataclass(frozen=True, slots=True, eq=False)
class ObjectStageIdentity:
    """An object as a stage-``1`` generalized element of its category."""

    parent: Category


@dataclass(frozen=True, slots=True, eq=False)
class ArrowStageIdentity:
    """A morphism as a stage-``[1]`` generalized element of its category."""

    parent: Category
    domain: ObjectOfCategory
    codomain: ObjectOfCategory


type CatElementRoleIdentity = GeneralCategoryPointIdentity | ObjectStageIdentity | ArrowStageIdentity


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
# proposition-valued.  The retained input is the input of the value's own root
# node.  Inputs for ancestor nodes are retained by their canonical target values.
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


def retained_object_input[Value: ObjectOfCategory, Datum](value: Value) -> ObjectConstructionInput[Value, Datum]:
    assert value in _object_inputs, f"{value!r} retains no object construction input"
    return _object_inputs[value]


def retained_element_input[Value: CategoryPoint, Datum](value: Value) -> ElementConstructionInput[Value, Datum]:
    assert value in _element_inputs, f"{value!r} retains no element construction input"
    return _element_inputs[value]


def retained_morphism_input[Value: MorphismOfCategory, Datum](value: Value) -> MorphismConstructionInput[Value, Datum]:
    assert value in _morphism_inputs, f"{value!r} retains no morphism construction input"
    return _morphism_inputs[value]


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
    cat_element_identity: ObjectStageIdentity
    steps: tuple[tuple[Node, Callable[[], None]], ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node) -> None:
        assert not any(_same_node(owner, node) for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        step = next(initialize for owner, initialize in self.steps if _same_node(owner, node))
        self.initialized.append(node)
        step()

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.steps if not any(_same_node(done, owner) for done in self.initialized)]
        assert not missing, f"the constructor chain did not initialize {missing[0].category!r}.{missing[0].role.value}"


@dataclass(slots=True)
class ElementConstructionContext:
    """One element identity and the closed node steps of its C3 constructor chain."""

    canonical_image: CategoryPoint
    identity: GeneralCategoryPointIdentity
    cat_element_identity: GeneralCategoryPointIdentity
    steps: tuple[tuple[Node, Callable[[], None]], ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node) -> None:
        assert not any(_same_node(owner, node) for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        step = next(initialize for owner, initialize in self.steps if _same_node(owner, node))
        self.initialized.append(node)
        step()

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.steps if not any(_same_node(done, owner) for done in self.initialized)]
        assert not missing, f"the constructor chain did not initialize {missing[0].category!r}.{missing[0].role.value}"


@dataclass(slots=True)
class MorphismConstructionContext:
    """One morphism identity and the closed node steps of its C3 constructor chain."""

    canonical_image: MorphismOfCategory
    identity: MorphismRoleIdentity
    cat_element_identity: ArrowStageIdentity
    steps: tuple[tuple[Node, Callable[[], None]], ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node) -> None:
        assert not any(_same_node(owner, node) for owner in self.initialized), (
            f"the {node.role.value} role of {node.category!r} initialized twice"
        )
        step = next(initialize for owner, initialize in self.steps if _same_node(owner, node))
        self.initialized.append(node)
        step()

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.steps if not any(_same_node(done, owner) for done in self.initialized)]
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
