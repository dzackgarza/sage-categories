"""State-bearing role construction (POL-KERNEL-029, POL-FUN-035).

Each public value retains one root input.  The input keeps the role identity,
the local typed datum, and the canonical public value as separate fields.
During initialization, one role-specific context holds every input that the
selected structural graph computed before the C3 constructor chain started.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sage.structure.coerce_dict import MonoDict

from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory

if TYPE_CHECKING:
    from sage_categories.cat.category import Category

__all__ = [
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
    "active_element_context",
    "active_morphism_context",
    "active_object_context",
    "deactivate_element_context",
    "deactivate_morphism_context",
    "deactivate_object_context",
    "retain_element_input",
    "retain_morphism_input",
    "retain_object_input",
    "retained_element_input",
    "retained_morphism_input",
    "retained_object_input",
]


@dataclass(frozen=True, slots=True, eq=False)
class ObjectRoleIdentity:
    """The kernel identity of an object in one category."""

    category: Category


@dataclass(frozen=True, slots=True, eq=False)
class ElementRoleIdentity:
    """The kernel identity of a generalized element."""

    defining_morphism: MorphismOfCategory


@dataclass(frozen=True, slots=True, eq=False)
class MorphismRoleIdentity:
    """The kernel identity of a morphism in one placement."""

    category: Category
    domain: ObjectOfCategory
    codomain: ObjectOfCategory


@dataclass(frozen=True, slots=True, eq=False)
class ObjectConstructionInput[Datum]:
    """The canonical object, its kernel identity, and one node's local datum."""

    canonical_image: ObjectOfCategory
    identity: ObjectRoleIdentity
    datum: Datum


@dataclass(frozen=True, slots=True, eq=False)
class ElementConstructionInput[Datum]:
    """The canonical generalized element, its identity, and one local datum."""

    canonical_image: ElementOfObject
    identity: ElementRoleIdentity
    datum: Datum


@dataclass(frozen=True, slots=True, eq=False)
class MorphismConstructionInput[Datum]:
    """The canonical morphism, its kernel identity, and one local datum."""

    canonical_image: MorphismOfCategory
    identity: MorphismRoleIdentity
    datum: Datum


# Identity-keyed storage is necessary because mathematical equality can be
# proposition-valued.  The retained input is the input of the value's own root
# node.  Inputs for ancestor nodes are retained by their canonical target values.
_object_inputs: MonoDict = MonoDict()
_element_inputs: MonoDict = MonoDict()
_morphism_inputs: MonoDict = MonoDict()


def retain_object_input(construction_input: ObjectConstructionInput) -> None:
    value = construction_input.canonical_image
    if value in _object_inputs:
        assert _object_inputs[value] is construction_input, f"{value!r} already retains a different object construction input"
        return
    _object_inputs[value] = construction_input


def retain_element_input(construction_input: ElementConstructionInput) -> None:
    value = construction_input.canonical_image
    if value in _element_inputs:
        assert _element_inputs[value] is construction_input, f"{value!r} already retains a different element construction input"
        return
    _element_inputs[value] = construction_input


def retain_morphism_input(construction_input: MorphismConstructionInput) -> None:
    value = construction_input.canonical_image
    if value in _morphism_inputs:
        assert _morphism_inputs[value] is construction_input, f"{value!r} already retains a different morphism construction input"
        return
    _morphism_inputs[value] = construction_input


def retained_object_input(value: ObjectOfCategory) -> ObjectConstructionInput:
    assert value in _object_inputs, f"{value!r} retains no object construction input"
    return _object_inputs[value]


def retained_element_input(value: ElementOfObject) -> ElementConstructionInput:
    assert value in _element_inputs, f"{value!r} retains no element construction input"
    return _element_inputs[value]


def retained_morphism_input(value: MorphismOfCategory) -> MorphismConstructionInput:
    assert value in _morphism_inputs, f"{value!r} retains no morphism construction input"
    return _morphism_inputs[value]


@dataclass(slots=True)
class ObjectConstructionContext:
    """All precomputed object inputs for one C3 constructor chain."""

    root: ObjectConstructionInput
    inputs: tuple[tuple[Category, ObjectConstructionInput], ...]
    initialized: list[Category] = field(default_factory=list)

    def input_for(self, category: Category) -> ObjectConstructionInput:
        return next(construction_input for owner, construction_input in self.inputs if owner is category)

    def begin(self, category: Category) -> ObjectConstructionInput:
        assert not any(owner is category for owner in self.initialized), f"the object role of {category!r} initialized twice"
        construction_input = self.input_for(category)
        self.initialized.append(category)
        return construction_input

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.inputs if not any(done is owner for done in self.initialized)]
        assert not missing, f"the object constructor chain did not initialize {missing[0]!r}"


@dataclass(slots=True)
class ElementConstructionContext:
    """All precomputed element inputs for one C3 constructor chain."""

    root: ElementConstructionInput
    inputs: tuple[tuple[Category, ElementConstructionInput], ...]
    initialized: list[Category] = field(default_factory=list)

    def input_for(self, category: Category) -> ElementConstructionInput:
        return next(construction_input for owner, construction_input in self.inputs if owner is category)

    def begin(self, category: Category) -> ElementConstructionInput:
        assert not any(owner is category for owner in self.initialized), f"the element role of {category!r} initialized twice"
        construction_input = self.input_for(category)
        self.initialized.append(category)
        return construction_input

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.inputs if not any(done is owner for done in self.initialized)]
        assert not missing, f"the element constructor chain did not initialize {missing[0]!r}"


@dataclass(slots=True)
class MorphismConstructionContext:
    """All precomputed morphism inputs for one C3 constructor chain."""

    root: MorphismConstructionInput
    inputs: tuple[tuple[Category, MorphismConstructionInput], ...]
    initialized: list[Category] = field(default_factory=list)

    def input_for(self, category: Category) -> MorphismConstructionInput:
        return next(construction_input for owner, construction_input in self.inputs if owner is category)

    def begin(self, category: Category) -> MorphismConstructionInput:
        assert not any(owner is category for owner in self.initialized), f"the morphism role of {category!r} initialized twice"
        construction_input = self.input_for(category)
        self.initialized.append(category)
        return construction_input

    def assert_complete(self) -> None:
        missing = [owner for owner, _ in self.inputs if not any(done is owner for done in self.initialized)]
        assert not missing, f"the morphism constructor chain did not initialize {missing[0]!r}"


_object_context: ContextVar[ObjectConstructionContext | None] = ContextVar("object construction context", default=None)
_element_context: ContextVar[ElementConstructionContext | None] = ContextVar("element construction context", default=None)
_morphism_context: ContextVar[MorphismConstructionContext | None] = ContextVar("morphism construction context", default=None)


def active_object_context() -> ObjectConstructionContext | None:
    return _object_context.get()


def active_element_context() -> ElementConstructionContext | None:
    return _element_context.get()


def active_morphism_context() -> MorphismConstructionContext | None:
    return _morphism_context.get()


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
