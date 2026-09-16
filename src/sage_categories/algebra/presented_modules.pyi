from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory

__all__ = [
    "finitely_presented_module",
    "presented_module_diagram",
    "presented_module_factor",
    "presented_module_presentation",
    "presented_module_projection",
    "presented_module_relation",
    "presented_module_zero",
    "relation_matrix_morphism",
]

type ModuleMap = MorphismCategory.ObjectType
type RelationMatrix = tuple[tuple[CategoryOfCategories.ElementType, ...], ...]

def relation_matrix_morphism(
    modules: ModuleCategory, entries: RelationMatrix
) -> ModuleMap: ...
def finitely_presented_module(
    modules: ModuleCategory, entries: RelationMatrix
) -> ModuleCategory.ObjectType: ...
def presented_module_diagram(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> Functor: ...
def presented_module_presentation(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> LimitConesCategory.ObjectType: ...
def presented_module_relation(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> ModuleMap: ...
def presented_module_zero(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> ModuleMap: ...
def presented_module_projection(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> ModuleMap: ...
def presented_module_factor(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    coequalizing: ModuleMap,
) -> ModuleMap: ...
