"""Static projection for affine global sections and comparisons."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.affine import AffineSchemesCategory
from sage_categories.geometry.affine_global_sections import (
    GlobalSections,
    affine_global_sections_comparison,
    affine_structure_sheaf_global_map,
    global_sections,
    global_sections_map,
    global_sections_spec_comparison,
)


def affine_global_section_types(
    scheme: AffineSchemesCategory.ObjectType,
    mapping: AffineSchemesCategory.MorphismType,
) -> None:
    assert_type(GlobalSections, Functor)
    assert_type(global_sections(scheme), CategoryOfCategories.ElementType)
    assert_type(global_sections_map(mapping), MorphismCategory.ObjectType)
    assert_type(
        affine_structure_sheaf_global_map(mapping),
        MorphismCategory.ObjectType,
    )
    assert_type(global_sections_spec_comparison, NaturalTransformation)
    assert_type(affine_global_sections_comparison, NaturalTransformation)
