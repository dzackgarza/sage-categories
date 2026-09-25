"""Static consumer for the unified scalar-general module API."""

from typing import assert_type

from sage.modules.free_module import FreeModule_generic
from sage.rings.integer import Integer

from sage_categories.algebra.modules import (
    finite_free_matrix_morphism,
    finite_free_module,
    finitely_presented_module,
    ordinary_modules,
    presented_module_factor,
    presented_module_projection,
    sage_module_from_engine,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def unified_module_types(
    scalars: MonoidCategory.ObjectType,
    coefficient: CategoryOfCategories.ElementType,
    target: ModuleCategory.ObjectType,
    coequalizing: MorphismCategory.ObjectType,
    engine_module: FreeModule_generic[Integer],
) -> None:
    modules = ordinary_modules(scalars)
    assert_type(modules, ModuleCategory)
    assert_type(modules.scalars(), MonoidCategory.ObjectType)
    free = finite_free_module(modules, 2)
    assert_type(free, ModuleCategory.ObjectType)
    matrix = ((coefficient, coefficient), (coefficient, coefficient))
    assert_type(
        finite_free_matrix_morphism(modules, free, free, matrix),
        MorphismCategory.ObjectType,
    )
    presented = finitely_presented_module(modules, ((coefficient,),))
    assert_type(presented, ModuleCategory.ObjectType)
    assert_type(presented_module_projection(modules, presented), MorphismCategory.ObjectType)
    assert_type(
        presented_module_factor(modules, presented, target, coequalizing),
        MorphismCategory.ObjectType,
    )
    assert_type(sage_module_from_engine(modules, engine_module), ModuleCategory.ObjectType)
