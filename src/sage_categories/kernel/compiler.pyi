from _typeshed import Incomplete
from collections.abc import Callable
from sage_categories.cat.category import Category as Category
from sage_categories.cat.functors import Functor as Functor
from sage_categories.kernel.construction import CategoryPointIdentity as CategoryPointIdentity, ElementConstructionContext as ElementConstructionContext, ElementConstructionInput as ElementConstructionInput, ElementRoleIdentity as ElementRoleIdentity, MorphismConstructionContext as MorphismConstructionContext, MorphismConstructionInput as MorphismConstructionInput, MorphismRoleIdentity as MorphismRoleIdentity, Node as Node, ObjectConstructionContext as ObjectConstructionContext, ObjectConstructionInput as ObjectConstructionInput, ObjectRoleIdentity as ObjectRoleIdentity, activate_element_context as activate_element_context, activate_morphism_context as activate_morphism_context, activate_object_context as activate_object_context, active_construction_context as active_construction_context, deactivate_element_context as deactivate_element_context, deactivate_morphism_context as deactivate_morphism_context, deactivate_object_context as deactivate_object_context, is_constructed as is_constructed, retain_element_input as retain_element_input, retain_morphism_input as retain_morphism_input, retain_object_by_datum as retain_object_by_datum, retain_object_input as retain_object_input, retained_element_input as retained_element_input, retained_input as retained_input, retained_morphism_input as retained_morphism_input, retained_object_by_datum as retained_object_by_datum, retained_object_input as retained_object_input, retained_values as retained_values
from sage_categories.kernel.roles import CategoryPoint as CategoryPoint, MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory, Role as Role, building_role_classes as building_role_classes, category_universal_class as category_universal_class, declaration_role as declaration_role, declared_roles as declared_roles, install_cat_element_root as install_cat_element_root, install_category_declaration_root as install_category_declaration_root, install_category_object_class as install_category_object_class, kernel_base as kernel_base, record_attribute_writes as record_attribute_writes, role_of as role_of
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, SageCategory as SageCategory, dynamic_class as dynamic_class, lazy_attribute as lazy_attribute
from typing import Concatenate, NamedTuple
type MethodResultProjection = tuple[str, tuple[tuple[int, int], ...]]
type MethodResultProjectionReader = Callable[[], dict[str, MethodResultProjection]]

def install_method_result_projection_reader(reader: MethodResultProjectionReader) -> None:
    ...

class SemanticCollisionError(Exception):
    ...

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

    def declared_method_result_projections(self) -> dict[str, MethodResultProjection]:
        ...

def compiler() -> _CompilerProjection:
    ...

def install_on_declaration[**P, R](local: type[CategoryPoint], name: str, member: Callable[Concatenate[CategoryPoint, P], R]) -> None:
    ...

def realize_implementation_class(value: CategoryPoint, category_type: type[CategoryPoint]) -> None:
    ...

def construct_category_value(instance: ObjectOfCategory) -> None:
    ...

def compile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def recompile_category(category: Category, functors: tuple[Functor, ...]) -> None:
    ...

def implement_category(category: Category, implementation: type[Category], selected_functors: tuple[Functor, ...], *, augment: bool) -> None:
    ...

def apply_level_shift(member: Category, placement: Category) -> None:
    ...

def _refine_implementation_class(value: CategoryPoint, role_class: type[CategoryPoint]) -> None:
    ...

def runtime_semantic_bases(runtime_class: type[CategoryPoint]) -> tuple[type[CategoryPoint], ...] | None:
    ...

def construct_category_singleton[Value: ObjectOfCategory](category_type: type[Value]) -> Value:
    ...
