"""The static projection preserves constructor data through Mor and fixed hom categories."""

from typing import assert_type

from sage_categories.cat.category import (
    Cat,
    Category,
    CategoryDeclaration,
    CategoryOfCategories,
)
from sage_categories.cat.declarations import CategoryFamily, DeclaredCategory
from sage_categories.cat.morphisms import FixedEndpointCategory, Mor, MorphismCategory
from sage_categories.cat.points import PointCategory


class FixedSource(CategoryOfCategories.ElementType):
    """A non-universal source type for the fixed-Hom projection consumer."""


class FixedTarget(CategoryOfCategories.ElementType):
    """A non-universal target type for the fixed-Hom projection consumer."""


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


def fixed_endpoint_dependence(
    category: Category[[str], [int]],
    source: FixedSource,
    target: FixedTarget,
) -> None:
    hom = Mor(category)(source, target)
    assert_type(
        hom,
        FixedEndpointCategory[[str], [int], FixedSource, FixedTarget],
    )
    assert_type(hom.domain(), FixedSource)
    assert_type(hom.codomain(), FixedTarget)
    assert_type(hom("arrow"), MorphismCategory.ObjectType)


def nullary_categories(member: CategoryOfCategories.ElementType) -> None:
    assert_type(Mor(PointCategory(member)), MorphismCategory[[], [], PointCategory.MorphismType])
    assert_type(Mor(DeclaredCategory("C")), MorphismCategory[[], [], DeclaredCategory.MorphismType])


def declared_category_interfaces(category: Category) -> None:
    declared = DeclaredCategory("Declared")
    family = CategoryFamily("Family", category)
    assert_type(Cat().declare(declared), DeclaredCategory)
    assert_type(Cat().declare_family(family), CategoryFamily)
    assert_type(Cat().declarations(), tuple[CategoryDeclaration | CategoryFamily, ...])
    assert_type(Cat().open_declaration(declared), DeclaredCategory | None)
    assert_type(Cat().implementation(declared), type[Category] | None)


def category_object_parameters(category: CategoryOfCategories.ObjectType[[str], [int]]) -> None:
    assert_type(Mor(category), MorphismCategory[[str], [int]])
