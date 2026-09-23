"""Static consumers for bimodule objects and their two-sided morphisms."""

from typing import assert_type

from sage_categories.cat.bimodules import BimoduleCategory
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
