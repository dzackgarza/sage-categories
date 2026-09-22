"""Static consumers for module transport and restriction of scalars."""

from typing import assert_type

from sage_categories.cat.functors import Functor
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


def module_restriction_types(
    modules: ModuleCategory,
    scalar_morphism: MorphismCategory.ObjectType,
) -> None:
    assert_type(modules.restriction(scalar_morphism), Functor)
