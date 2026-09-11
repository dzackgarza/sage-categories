"""The static projection retains concrete functor endpoints and their action roles."""

from typing import assert_type

from sage_categories.cat.functors import Fun
from sage_categories.sets.finite import SetsCategory
from sage_categories.sets.natural import PositiveIntegersCategory


def functor_action_parameters(
    source: PositiveIntegersCategory,
    target: SetsCategory,
    member_object: PositiveIntegersCategory.ObjectType,
    morphism: PositiveIntegersCategory.MorphismType,
    target_object: SetsCategory.ObjectType,
    target_morphism: SetsCategory.MorphismType,
) -> None:
    functor = Fun(source, target)(lambda _value: target_object, lambda _arrow: target_morphism)
    assert_type(functor.domain(), PositiveIntegersCategory)
    assert_type(functor.codomain(), SetsCategory)
    assert_type(functor.on_object(member_object), SetsCategory.ObjectType)
    assert_type(functor.on_morphism(morphism), SetsCategory.MorphismType)
