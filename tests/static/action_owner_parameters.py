"""Supplied actions keep the acting and acted-on category types distinct."""

from typing import assert_type

from sage_categories.cat.category import Category
from sage_categories.cat.monoidal import (
    Actions,
    ActionsCategory,
    MonoidalStructuresCategory,
)


class ActingCategory(Category[[], []]):
    pass


class ActedOnCategory(Category[[], []]):
    pass


def action_owner_parameters(
    monoidal: MonoidalStructuresCategory.ObjectType[ActingCategory],
    acted_on: ActedOnCategory,
    action: ActionsCategory.ObjectType[ActingCategory, ActedOnCategory],
) -> None:
    assert_type(Actions(monoidal, acted_on), ActionsCategory[ActingCategory, ActedOnCategory])
    assert_type(action.monoidal_structure().underlying_category(), ActingCategory)
    assert_type(action.underlying_category(), ActedOnCategory)
