from collections.abc import Callable
from contextvars import Token
from dataclasses import dataclass, field
from sage_categories.cat.category import Category
from sage_categories.kernel.compiler import Node
from sage_categories.kernel.roles import CategoryPoint, MorphismOfCategory, ObjectOfCategory
__all__ = ['ObjectRoleIdentity', 'ElementRoleIdentity', 'CategoryPointIdentity', 'CatElementRoleIdentity', 'MorphismRoleIdentity', 'ObjectConstructionInput', 'ElementConstructionInput', 'MorphismConstructionInput', 'retain_object_input', 'retain_element_input', 'retain_morphism_input', 'retained_objects', 'is_constructed', 'retained_object_input', 'retained_element_input', 'retained_morphism_input', 'retained_object_by_datum', 'retain_object_by_datum', 'retained_input', 'ObjectConstructionContext', 'ElementConstructionContext', 'MorphismConstructionContext', 'active_object_context', 'active_element_context', 'active_morphism_context', 'active_construction_context', 'activate_object_context', 'activate_element_context', 'activate_morphism_context', 'deactivate_object_context', 'deactivate_element_context', 'deactivate_morphism_context']

@dataclass(frozen=True, slots=True, eq=False)
class ObjectRoleIdentity:
    category: Category

@dataclass(frozen=True, slots=True, eq=False)
class ElementRoleIdentity:
    defining_morphism: MorphismOfCategory

@dataclass(frozen=True, slots=True, eq=False)
class CategoryPointIdentity:
    parent: Category
type CatElementRoleIdentity = ElementRoleIdentity | CategoryPointIdentity

@dataclass(frozen=True, slots=True, eq=False)
class MorphismRoleIdentity:
    category: Category
    domain: ObjectOfCategory
    codomain: ObjectOfCategory

@dataclass(frozen=True, slots=True, eq=False)
class ObjectConstructionInput[Value: ObjectOfCategory, Datum]:
    canonical_image: Value
    identity: ObjectRoleIdentity
    datum: Datum

@dataclass(frozen=True, slots=True, eq=False)
class ElementConstructionInput[Value: CategoryPoint, Datum]:
    canonical_image: Value
    identity: CatElementRoleIdentity
    datum: Datum

@dataclass(frozen=True, slots=True, eq=False)
class MorphismConstructionInput[Value: MorphismOfCategory, Datum]:
    canonical_image: Value
    identity: MorphismRoleIdentity
    datum: Datum

def retain_object_input[Value: ObjectOfCategory, Datum](construction_input: ObjectConstructionInput[Value, Datum]) -> None:
    ...

def retain_element_input[Value: CategoryPoint, Datum](construction_input: ElementConstructionInput[Value, Datum]) -> None:
    ...

def retain_morphism_input[Value: MorphismOfCategory, Datum](construction_input: MorphismConstructionInput[Value, Datum]) -> None:
    ...

def retained_objects(category: Category) -> tuple[ObjectOfCategory, ...]:
    ...

def is_constructed(value: ObjectOfCategory) -> bool:
    ...

def retained_object_input[Value: ObjectOfCategory, Datum](value: Value) -> ObjectConstructionInput[Value, Datum]:
    ...

def retained_element_input[Value: CategoryPoint, Datum](value: Value) -> ElementConstructionInput[Value, Datum]:
    ...

def retained_morphism_input[Value: MorphismOfCategory, Datum](value: Value) -> MorphismConstructionInput[Value, Datum]:
    ...

def retained_object_by_datum[Datum](category: Category, datum: Datum) -> ObjectOfCategory | None:
    ...

def retain_object_by_datum[Value: ObjectOfCategory, Datum](category: Category, datum: Datum, value: Value) -> None:
    ...

def retained_input[Value: CategoryPoint, Datum](value: Value) -> ObjectConstructionInput[Value, Datum] | ElementConstructionInput[Value, Datum] | MorphismConstructionInput[Value, Datum]:
    ...

@dataclass(slots=True)
class ObjectConstructionContext:
    canonical_image: ObjectOfCategory
    identity: ObjectRoleIdentity
    cat_element_identity: CategoryPointIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        ...

    def assert_complete(self) -> None:
        ...

@dataclass(slots=True)
class ElementConstructionContext:
    canonical_image: CategoryPoint
    identity: ElementRoleIdentity
    cat_element_identity: ElementRoleIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        ...

    def assert_complete(self) -> None:
        ...

@dataclass(slots=True)
class MorphismConstructionContext:
    canonical_image: MorphismOfCategory
    identity: MorphismRoleIdentity
    cat_element_identity: CategoryPointIdentity
    nodes: tuple[Node, ...]
    initialized: list[Node] = field(default_factory=list)

    def run(self, node: Node, initialize: Callable[[], None]) -> None:
        ...

    def assert_complete(self) -> None:
        ...

def active_object_context() -> ObjectConstructionContext | None:
    ...

def active_element_context() -> ElementConstructionContext | None:
    ...

def active_morphism_context() -> MorphismConstructionContext | None:
    ...

def active_construction_context(value: CategoryPoint) -> ObjectConstructionContext | ElementConstructionContext | MorphismConstructionContext | None:
    ...

def activate_object_context(context: ObjectConstructionContext) -> Token[ObjectConstructionContext | None]:
    ...

def activate_element_context(context: ElementConstructionContext) -> Token[ElementConstructionContext | None]:
    ...

def activate_morphism_context(context: MorphismConstructionContext) -> Token[MorphismConstructionContext | None]:
    ...

def deactivate_object_context(token: Token[ObjectConstructionContext | None]) -> None:
    ...

def deactivate_element_context(token: Token[ElementConstructionContext | None]) -> None:
    ...

def deactivate_morphism_context(token: Token[MorphismConstructionContext | None]) -> None:
    ...
