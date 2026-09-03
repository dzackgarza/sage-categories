from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.kernel.roles import CategoryPoint, ObjectOfCategory, Role
from sage_categories.kernel.sage_runtime import SageCategory, lazy_attribute
from typing import Concatenate, NamedTuple
__all__ = ['SemanticCollisionError', 'Node', 'node', 'same_node', 'inheriting_functors', 'declared_inheritance', 'declared_subtyping', 'compiler', 'install_on_declaration', 'construct_category_value', 'compile_category', 'recompile_category', 'apply_level_shift']

class SemanticCollisionError(Exception):
    ...

class _KernelRoleRootCategory(SageCategory):

    def __init__(self, role: Role, root: type[CategoryPoint]) -> None:
        ...

    def super_categories(self) -> list[SageCategory]:
        ...

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        ...

class _RuntimeImplementationCategory(SageCategory):
    ParentMethods: Incomplete

    def __init__(self, current: Node, targets: tuple[SageCategory, ...]) -> None:
        ...

    def super_categories(self) -> list[SageCategory]:
        ...

    @lazy_attribute
    def parent_class(self) -> type[CategoryPoint]:
        ...

class Node(NamedTuple):
    category: Category
    role: Role

def node(category: Category, role: Role) -> Node:
    ...

def same_node(first: Node, second: Node) -> bool:
    ...

def inheriting_functors(category: Category) -> tuple[Functor, ...]:
    ...

def declared_inheritance(category: Category, role: Role) -> tuple[type[CategoryPoint], ...]:
    ...

def declared_subtyping(category: Category, role: Role) -> tuple[Category, ...]:
    ...

class _CompilerProjection:

    def declared_inheritance(self) -> dict[str, dict[str, tuple[str, ...]]]:
        ...

    def declared_subtyping(self) -> dict[str, dict[str, tuple[str, ...]]]:
        ...

def compiler() -> _CompilerProjection:
    ...

def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: Callable[Concatenate[CategoryPoint, P], R]) -> None:
    ...

class _NodeRuntime[Value: CategoryPoint, Datum](NamedTuple):
    initializer: Callable[[Value, Datum], None]
    owner: type[Value]
    written: bool
type _ImageDatum = Callable[[Functor, CategoryPoint], tuple[Node, object]]

class _SelectedAction(NamedTuple):
    functor: Functor
    owner: Node
    target: Node
    datum: object
    representative: CategoryPoint

def construct_category_value(instance: ObjectOfCategory) -> None:
    ...

def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def apply_level_shift(member: Category, placement: Category) -> None:
    ...
