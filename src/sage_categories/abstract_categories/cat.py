"""``Cat``: the category whose objects are categories."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sage_categories.category import Category
from sage_categories.values import (
    MathematicalElement,
    MathematicalObject,
    MembershipInput,
    registered_value,
)

if TYPE_CHECKING:
    from sage_categories.abstract_categories.hom_categories import HomCategory


class CategoryOfCategories(Category):
    """The represented universe of categories."""

    def __init__(self) -> None:
        MathematicalObject.__init__(self, category=None)
        self._initialize_category(Category, MathematicalElement)

    def _hom_category_type(self) -> type[HomCategory]:
        from sage_categories.abstract_categories.functors import FunctorCategory

        return FunctorCategory

    def __contains__(self, candidate: MembershipInput) -> bool:
        value = registered_value(candidate)
        return value is not None and value._belongs_to(self)

    def _belongs_to(self, category: Category) -> bool:
        return False

    def __repr__(self) -> str:
        return "Cat"


_CAT = CategoryOfCategories()


def Cat() -> CategoryOfCategories:
    """Return the category of categories."""
    return _CAT
