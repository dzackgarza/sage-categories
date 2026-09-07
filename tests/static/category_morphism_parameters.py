"""The static projection preserves constructor data through Mor and fixed hom categories."""

from typing import assert_type

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.declarations import DeclaredCategory
from sage_categories.cat.morphisms import FixedEndpointCategory, Mor, MorphismCategory
from sage_categories.cat.points import PointCategory


def constructor_parameters(
    category: Category[[str], [int]],
    source: CategoryOfCategories.ElementType,
    target: CategoryOfCategories.ElementType,
) -> None:
    morphisms = Mor(category)
    assert_type(morphisms, MorphismCategory[[str], [int]])
    hom = morphisms(source, target)
    assert_type(hom, FixedEndpointCategory[[str], [int]])
    assert_type(hom("arrow"), MorphismCategory.ObjectType)
    assert_type(Mor(0, category), Category[[str], [int]])
    assert_type(Mor(1, category), MorphismCategory[[str], [int]])
    assert_type(Mor(2, category), MorphismCategory[[int], []])


def nullary_categories(member: CategoryOfCategories.ElementType) -> None:
    assert_type(Mor(PointCategory(member)), MorphismCategory[[], []])
    assert_type(Mor(DeclaredCategory("C")), MorphismCategory[[], []])
