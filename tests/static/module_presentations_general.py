"""Static consumer for scalar-general finite module presentations."""

from typing import assert_type

from sage_categories.algebra.presented_modules import (
    finitely_presented_module,
    presented_module_diagram,
    presented_module_factor,
    presented_module_presentation,
    presented_module_projection,
    presented_module_relation,
    presented_module_zero,
    relation_matrix_morphism,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory


def presentation_types(
    modules: ModuleCategory,
    coefficient: CategoryOfCategories.ElementType,
    target: ModuleCategory.ObjectType,
    coequalizing: MorphismCategory.ObjectType,
) -> None:
    matrix = ((coefficient,),)
    assert_type(relation_matrix_morphism(modules, matrix), MorphismCategory.ObjectType)
    module = finitely_presented_module(modules, matrix)
    assert_type(module, ModuleCategory.ObjectType)
    assert_type(presented_module_diagram(modules, module), Functor)
    assert_type(presented_module_presentation(modules, module), LimitConesCategory.ObjectType)
    assert_type(presented_module_relation(modules, module), MorphismCategory.ObjectType)
    assert_type(presented_module_zero(modules, module), MorphismCategory.ObjectType)
    assert_type(presented_module_projection(modules, module), MorphismCategory.ObjectType)
    assert_type(presented_module_factor(modules, module, target, coequalizing), MorphismCategory.ObjectType)
