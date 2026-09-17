"""Static domains for topological points, valued points, and schemes over a base."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.schemes import SchemesCategory


def check_scheme_points_and_base(
    scheme: SchemesCategory.ObjectType,
    base: SchemesCategory.ObjectType,
    ring: CategoryOfCategories.ElementType,
    structure_map: SchemesCategory.MorphismType,
) -> None:
    assert_type(scheme.underlying_points(), CategoryOfCategories.ElementType)
    assert_type(scheme.valued_points(ring), MorphismCategory)
    assert_type(scheme.categorical_points(), MorphismCategory)
    assert_type(scheme.over(base, structure_map), CategoryOfCategories.ElementType)
