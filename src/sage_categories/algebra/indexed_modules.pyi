from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory
__all__ = ['integer_scalar_monoid', 'integer_regular_module', 'indexed_free_integer_module', 'indexed_free_integer_element', 'indexed_free_integer_support', 'indexed_free_integer_coefficients', 'indexed_free_integer_homomorphism']

@dataclass(frozen=True, eq=False, slots=True)
class _IndexedFreeIntegerModuleData:
    modules: ModuleCategory
    carrier: CategoryOfCategories.ElementType

def integer_scalar_monoid() -> CategoryOfCategories.ElementType:
    ...

def integer_regular_module() -> ModuleCategory.ObjectType:
    ...

def indexed_free_integer_module(index_set: CategoryOfCategories.ElementType) -> ModuleCategory.ObjectType:
    ...

def indexed_free_integer_element(module: ModuleCategory.ObjectType, terms: Mapping[Hashable, int]) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_integer_support(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
    ...

def indexed_free_integer_coefficients(module: ModuleCategory.ObjectType, element: CategoryOfCategories.ElementType) -> dict[Hashable, int]:
    ...

def indexed_free_integer_homomorphism(source: ModuleCategory.ObjectType, target: ModuleCategory.ObjectType, basis_image) -> MorphismCategory.ObjectType:
    ...
