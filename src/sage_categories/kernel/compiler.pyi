from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.cat.category import Category as SageCategory
from sage.misc.lazy_attribute import lazy_attribute
from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.kernel.roles import CategoryPoint, Role
from typing import Concatenate, NamedTuple
__all__ = ['SemanticCollisionError', 'Node', 'node', 'same_node', 'declared_inheritance', 'declared_subtyping', 'compiler', 'install_on_declaration', 'compile_category', 'recompile_category', 'apply_level_shift']

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

def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def apply_level_shift(member: Category, placement: Category) -> None:
    ...
