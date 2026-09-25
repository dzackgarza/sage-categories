"""Static consumer for generic finite-product presentations and their maps."""

from typing import assert_type

from sage_categories.cat.calculus import (
    finite_product_data,
    finite_product_morphism,
    finite_product_projection,
)
from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.limit_basis import (
    coequalizer_factor,
    coequalizer_presentation,
    equalizer_factor,
    equalizer_presentation,
)
from sage_categories.cat.morphisms import MorphismCategory


def finite_product_calculus_types(
    base: Category,
    first: CategoryOfCategories.ElementType,
    second: CategoryOfCategories.ElementType,
    source: CategoryOfCategories.ElementType,
    first_component: MorphismCategory.ObjectType,
    second_component: MorphismCategory.ObjectType,
    equalizer_apex: CategoryOfCategories.ElementType,
    equalizer_source: CategoryOfCategories.ElementType,
    equalizing_arrow: MorphismCategory.ObjectType,
    coequalizer_projection: MorphismCategory.ObjectType,
    coequalizing_arrow: MorphismCategory.ObjectType,
) -> None:
    data = finite_product_data(base, (first, second))
    assert_type(data, LimitConesCategory.ObjectType)
    assert_type(finite_product_projection(data, 0), MorphismCategory.ObjectType)
    assert_type(
        finite_product_morphism(data, source, (first_component, second_component)),
        MorphismCategory.ObjectType,
    )
    equalizer = equalizer_presentation(base, equalizer_apex, equalizer_source)
    assert_type(equalizer, LimitConesCategory.ObjectType)
    assert_type(equalizer_factor(equalizer, equalizing_arrow), MorphismCategory.ObjectType)
    coequalizer = coequalizer_presentation(base, coequalizer_projection)
    assert_type(coequalizer, LimitConesCategory.ObjectType)
    assert_type(coequalizer_factor(coequalizer, coequalizing_arrow), MorphismCategory.ObjectType)
