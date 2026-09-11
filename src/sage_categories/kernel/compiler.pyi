from collections.abc import Callable
from typing import Concatenate

from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Functor as Functor
from sage_categories.kernel.construction import (
    CategoryPointIdentity as CategoryPointIdentity,
)
from sage_categories.kernel.construction import (
    ElementConstructionContext as ElementConstructionContext,
)
from sage_categories.kernel.construction import (
    ElementConstructionInput as ElementConstructionInput,
)
from sage_categories.kernel.construction import (
    ElementRoleIdentity as ElementRoleIdentity,
)
from sage_categories.kernel.construction import (
    MorphismConstructionContext as MorphismConstructionContext,
)
from sage_categories.kernel.construction import (
    MorphismConstructionInput as MorphismConstructionInput,
)
from sage_categories.kernel.construction import (
    MorphismRoleIdentity as MorphismRoleIdentity,
)
from sage_categories.kernel.construction import (
    Node as Node,
)
from sage_categories.kernel.construction import (
    ObjectConstructionContext as ObjectConstructionContext,
)
from sage_categories.kernel.construction import (
    ObjectConstructionInput as ObjectConstructionInput,
)
from sage_categories.kernel.construction import (
    ObjectRoleIdentity as ObjectRoleIdentity,
)
from sage_categories.kernel.construction import (
    activate_element_context as activate_element_context,
)
from sage_categories.kernel.construction import (
    activate_morphism_context as activate_morphism_context,
)
from sage_categories.kernel.construction import (
    activate_object_context as activate_object_context,
)
from sage_categories.kernel.construction import (
    active_construction_context as active_construction_context,
)
from sage_categories.kernel.construction import (
    deactivate_element_context as deactivate_element_context,
)
from sage_categories.kernel.construction import (
    deactivate_morphism_context as deactivate_morphism_context,
)
from sage_categories.kernel.construction import (
    deactivate_object_context as deactivate_object_context,
)
from sage_categories.kernel.construction import (
    is_constructed as is_constructed,
)
from sage_categories.kernel.construction import (
    retain_element_input as retain_element_input,
)
from sage_categories.kernel.construction import (
    retain_morphism_input as retain_morphism_input,
)
from sage_categories.kernel.construction import (
    retain_object_by_datum as retain_object_by_datum,
)
from sage_categories.kernel.construction import (
    retain_object_input as retain_object_input,
)
from sage_categories.kernel.construction import (
    retained_element_input as retained_element_input,
)
from sage_categories.kernel.construction import (
    retained_input as retained_input,
)
from sage_categories.kernel.construction import (
    retained_morphism_input as retained_morphism_input,
)
from sage_categories.kernel.construction import (
    retained_object_by_datum as retained_object_by_datum,
)
from sage_categories.kernel.construction import (
    retained_object_input as retained_object_input,
)
from sage_categories.kernel.construction import (
    retained_values as retained_values,
)
from sage_categories.kernel.roles import (
    CategoryPoint as CategoryPoint,
)
from sage_categories.kernel.roles import (
    MorphismOfCategory as MorphismOfCategory,
)
from sage_categories.kernel.roles import (
    ObjectOfCategory as ObjectOfCategory,
)
from sage_categories.kernel.roles import (
    Role as Role,
)
from sage_categories.kernel.roles import (
    building_role_classes as building_role_classes,
)
from sage_categories.kernel.roles import (
    declaration_role as declaration_role,
)
from sage_categories.kernel.roles import (
    install_cat_element_root as install_cat_element_root,
)
from sage_categories.kernel.roles import (
    install_category_declaration_root as install_category_declaration_root,
)
from sage_categories.kernel.roles import (
    install_category_object_class as install_category_object_class,
)
from sage_categories.kernel.roles import (
    kernel_base as kernel_base,
)
from sage_categories.kernel.roles import (
    record_attribute_writes as record_attribute_writes,
)
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict
from sage_categories.kernel.sage_runtime import SageCategory as SageCategory
from sage_categories.kernel.sage_runtime import dynamic_class as dynamic_class
from sage_categories.kernel.sage_runtime import lazy_attribute as lazy_attribute

__all__ = [
    "Node",
    "SemanticCollisionError",
    "apply_level_shift",
    "compile_category",
    "compiler",
    "construct_category_value",
    "declared_inheritance",
    "declared_subtyping",
    "implement_category",
    "inheriting_functors",
    "install_method_result_projection_reader",
    "install_on_declaration",
    "node",
    "realize_implementation_class",
    "recompile_category",
    "same_node",
]
type MethodResultProjection = tuple[str, tuple[tuple[int, int], ...]]
type MethodResultProjectionReader = Callable[[], dict[str, MethodResultProjection]]

def install_method_result_projection_reader(reader: MethodResultProjectionReader) -> None: ...

class SemanticCollisionError(Exception): ...

def node(category: Category, role: Role) -> Node: ...
def same_node(first: Node, second: Node) -> bool: ...
def inheriting_functors(category: Category) -> tuple[Functor, ...]: ...
def declared_inheritance(category: Category, role: Role) -> tuple[type[CategoryPoint], ...]: ...
def declared_subtyping(category: Category, role: Role) -> tuple[Category, ...]: ...

class _CompilerProjection:
    def declared_inheritance(self) -> dict[str, dict[str, tuple[str, ...]]]: ...
    def declared_subtyping(self) -> dict[str, dict[str, tuple[str, ...]]]: ...
    def declared_method_result_projections(self) -> dict[str, MethodResultProjection]: ...

def compiler() -> _CompilerProjection: ...
def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: Callable[Concatenate[CategoryPoint, P], R]) -> None: ...
def realize_implementation_class(value: CategoryPoint, category_type: type[CategoryPoint]) -> None: ...
def construct_category_value(instance: ObjectOfCategory) -> None: ...
def compile_category(category: Category, functors: tuple[Functor, ...]) -> None: ...
def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None: ...
def implement_category(category: Category, implementation: type[Category], selected_functors: tuple[Functor, ...], *, augment: bool) -> None: ...
def apply_level_shift(member: Category, placement: Category) -> None: ...
def _refine_implementation_class(value: CategoryPoint, role_class: type[CategoryPoint]) -> None: ...
def runtime_semantic_bases(runtime_class: type[CategoryPoint]) -> tuple[type[CategoryPoint], ...] | None: ...
def construct_category_singleton[Value: ObjectOfCategory](category_type: type[Value]) -> Value: ...
