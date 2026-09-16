from collections.abc import Callable
from dataclasses import dataclass

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory

__all__ = [
    "finite_free_basis",
    "finite_free_basis_family",
    "finite_free_injection",
    "finite_free_matrix_morphism",
    "finite_free_module",
    "finite_free_projection",
    "free_module_homomorphism",
    "ordinary_modules",
    "regular_module",
]

type ModuleMap = MorphismCategory.ObjectType
type PairRule = Callable[[tuple[ModuleMap, ...]], ModuleMap]
type BasisImageRule = Callable[[CategoryOfCategories.ElementType], ModuleMap]

def ordinary_modules(scalars: MonoidCategory.ObjectType) -> ModuleCategory: ...
def regular_module(modules: ModuleCategory) -> ModuleCategory.ObjectType: ...

@dataclass(frozen=True, eq=False, slots=True)
class _FreeStage:
    module: ModuleCategory.ObjectType
    injections: tuple[ModuleMap, ...]
    projections: tuple[ModuleMap, ...]
    pair: PairRule
    copair: PairRule

def finite_free_module(
    modules: ModuleCategory, rank: int
) -> ModuleCategory.ObjectType: ...
def finite_free_basis(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> CategoryOfCategories.ElementType: ...
def finite_free_basis_family(
    modules: ModuleCategory, module: ModuleCategory.ObjectType
) -> Functor: ...
def finite_free_injection(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    index: CategoryOfCategories.ElementType,
) -> ModuleMap: ...
def finite_free_projection(
    modules: ModuleCategory,
    module: ModuleCategory.ObjectType,
    index: CategoryOfCategories.ElementType,
) -> ModuleMap: ...
def free_module_homomorphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    basis_image: BasisImageRule,
) -> ModuleMap: ...
def finite_free_matrix_morphism(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    target: ModuleCategory.ObjectType,
    entries: tuple[tuple[CategoryOfCategories.ElementType, ...], ...],
) -> ModuleMap: ...
