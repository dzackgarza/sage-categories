"""Static consumer for generic finite-product presentations and their maps."""

from typing import assert_type

from sage_categories.cat.calculus import (
    finite_product_data,
    finite_product_morphism,
    finite_product_projection,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.morphisms import MorphismCategory


def finite_product_calculus_types(
    base: Category,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    source: CategoryOfCategories.ElementType,
    first_component: MorphismCategory.ObjectType,
    second_component: MorphismCategory.ObjectType,
) -> None:
    data = finite_product_data(base, (first, second))
    assert_type(data, LimitConesCategory.ObjectType)
    assert_type(finite_product_projection(data, 0), MorphismCategory.ObjectType)
    assert_type(
        finite_product_morphism(data, source, (first_component, second_component)),
        MorphismCategory.ObjectType,
    )
