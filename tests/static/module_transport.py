"""Static consumer for module transport and its lifted carrier isomorphism."""

from typing import assert_type

from sage_categories.cat.modules import ModuleCategory
from sage_categories.cat.morphisms import MorphismCategory


def module_transport_types(
    modules: ModuleCategory,
    source: ModuleCategory.ObjectType,
    isomorphism: MorphismCategory.ObjectType,
) -> None:
    transported = modules.transport(source, isomorphism)
    assert_type(transported, ModuleCategory.ObjectType)
    assert_type(transported.action(), MorphismCategory.ObjectType)
    assert_type(
        modules.homomorphism(source, transported, isomorphism),
        ModuleCategory.MorphismType,
    )
