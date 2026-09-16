"""Static consumer for scalar-general finite free modules."""

from collections.abc import Callable
from typing import assert_type

from sage_categories.algebra.free_modules import (
    finite_free_basis,
    finite_free_basis_family,
    finite_free_injection,
    finite_free_matrix_morphism,
    finite_free_module,
    finite_free_projection,
    free_module_homomorphism,
    ordinary_modules,
    regular_module,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def free_module_types(
    scalars: MonoidCategory.ObjectType,
    module: ModuleCategory.ObjectType,
    basis_index: CategoryOfCategories.ElementType,
    coefficient: CategoryOfCategories.ElementType,
    basis_image: Callable[[CategoryOfCategories.ElementType], MorphismCategory.ObjectType],
) -> None:
    modules = ordinary_modules(scalars)
    assert_type(modules, ModuleCategory)
    assert_type(regular_module(modules), ModuleCategory.ObjectType)
    assert_type(finite_free_module(modules, 3), ModuleCategory.ObjectType)
    assert_type(finite_free_basis(modules, module), CategoryOfCategories.ElementType)
    assert_type(finite_free_basis_family(modules, module), Functor)
    assert_type(finite_free_injection(modules, module, basis_index), MorphismCategory.ObjectType)
    assert_type(finite_free_projection(modules, module, basis_index), MorphismCategory.ObjectType)
    assert_type(free_module_homomorphism(modules, module, module, basis_image), MorphismCategory.ObjectType)
    assert_type(finite_free_matrix_morphism(modules, module, module, ((coefficient,),)), MorphismCategory.ObjectType)
