"""Static consumers for bimodule objects and their two-sided morphisms."""

from typing import assert_type

from sage_categories.cat.bimodules import (
    BimoduleCategory,
    fixed_tensor_functor,
    induced_left_action,
    induced_right_action,
    relative_tensor,
    relative_tensor_factor,
    relative_tensor_morphism,
    relative_tensor_presentation,
    relative_tensor_preserved_factor,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory


def bimodule_object_types(
    bimodules: BimoduleCategory,
    left_action: MorphismCategory.ObjectType,
    right_action: MorphismCategory.ObjectType,
) -> None:
    module = bimodules(left_action, right_action)
    assert_type(module, BimoduleCategory.ObjectType)
    assert_type(module.left_action(), MorphismCategory.ObjectType)
    assert_type(module.right_action(), MorphismCategory.ObjectType)


def bimodule_morphism_types(
    bimodules: BimoduleCategory,
    source: BimoduleCategory.ObjectType,
    target: BimoduleCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
) -> None:
    assert_type(
        bimodules.homomorphism(source, target, arrow),
        BimoduleCategory.MorphismType,
    )


def relative_tensor_calculus_types(
    monoidal: MonoidalStructuresCategory.ObjectType,
    middle: CategoryOfCategories.ElementType,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    scalars: CategoryOfCategories.ElementType,
    right_action: MorphismCategory.ObjectType,
    left_action: MorphismCategory.ObjectType,
    projection: MorphismCategory.ObjectType,
    target_projection: MorphismCategory.ObjectType,
    first_map: MorphismCategory.ObjectType,
    second_map: MorphismCategory.ObjectType,
    arrow: MorphismCategory.ObjectType,
    preserving: Functor,
) -> None:
    assert_type(fixed_tensor_functor(monoidal, first, "left"), Functor)
    assert_type(fixed_tensor_functor(monoidal, second, "right"), Functor)
    assert_type(relative_tensor(monoidal, middle, right_action, left_action), MorphismCategory.ObjectType)
    assert_type(relative_tensor_presentation(monoidal, projection), LimitConesCategory.ObjectType)
    assert_type(relative_tensor_factor(monoidal, projection, arrow), MorphismCategory.ObjectType)
    assert_type(relative_tensor_preserved_factor(monoidal, projection, preserving, arrow), MorphismCategory.ObjectType)
    assert_type(induced_left_action(monoidal, projection, scalars, second, left_action), MorphismCategory.ObjectType)
    assert_type(induced_right_action(monoidal, projection, first, scalars, right_action), MorphismCategory.ObjectType)
    assert_type(
        relative_tensor_morphism(monoidal, projection, target_projection, first_map, second_map),
        MorphismCategory.ObjectType,
    )
