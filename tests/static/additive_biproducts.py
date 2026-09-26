"""Static consumer for category-owned additive biproduct operations."""

from typing import assert_type

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory


def additive_biproduct_types(
    category: Category,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
) -> None:
    assert_type(category.biproduct(first, second), CategoryOfCategories.ElementType)
    assert_type(category.zero_morphism(first, second), MorphismCategory.ObjectType)
