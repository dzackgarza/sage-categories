"""Static consumers for module transport and restriction of scalars."""

from typing import assert_type

from sage_categories.cat.category import Category
from sage_categories.cat.functors import Functor
from sage_categories.cat.modules import ModuleCategory, Modules
from sage_categories.cat.monoidal import ActionsCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


class ActingCategory(Category[[], []]):
    pass


class ActedOnCategory(Category[[], []]):
    pass


def module_owner_parameters(
    scalars: MonoidCategory.ObjectType,
    action: ActionsCategory.ObjectType[ActingCategory, ActedOnCategory],
) -> None:
    modules = Modules(scalars, action)
    assert_type(modules, ModuleCategory[ActingCategory, ActedOnCategory])
    assert_type(modules.actegory(), ActionsCategory.ObjectType[ActingCategory, ActedOnCategory])
    assert_type(modules.underlying_category(), ActedOnCategory)


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
