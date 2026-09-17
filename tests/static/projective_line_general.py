"""Exact public types for the projective line through finite affine gluing."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.slices import SliceLikeCategory
from sage_categories.geometry import (
    AffineOpenCategory,
    AffineSchemesCategory,
    ProjectiveLinePresentation,
    SchemesCategory,
    SchemeOpenCategory,
    projective_line,
)
from sage_categories.geometry.schemes import AffineOpenChart, FiniteAffineGluing
from sage_categories.geometry.sheaves import RingPresheaf, RingSheaf


def check_projective_line_general(field: CategoryOfCategories.ElementType) -> None:
    presentation = projective_line(field)
    assert_type(presentation, ProjectiveLinePresentation)
    assert_type(presentation.scheme, SchemesCategory.ObjectType[SchemeOpenCategory.ObjectType])
    assert_type(presentation.scheme.finite_affine_gluing(), FiniteAffineGluing)
    assert_type(presentation.scheme.affine_cover(), tuple[AffineOpenChart, ...])
    assert_type(presentation.left_chart, AffineSchemesCategory.ObjectType)
    assert_type(presentation.right_chart, AffineSchemesCategory.ObjectType)
    assert_type(presentation.left_inclusion, SchemesCategory.MorphismType)
    assert_type(presentation.right_inclusion, SchemesCategory.MorphismType)
    assert_type(presentation.chart_swap, SchemesCategory.MorphismType)
    assert_type(presentation.structure_sheaf, RingSheaf[SchemeOpenCategory.ObjectType])
    assert_type(
        presentation.structure_sheaf.presheaf,
        RingPresheaf[SchemeOpenCategory.ObjectType],
    )
    assert_type(presentation.left_scheme_open, SchemeOpenCategory.ObjectType)
    assert_type(presentation.right_scheme_open, SchemeOpenCategory.ObjectType)
    assert_type(presentation.overlap_scheme_open, SchemeOpenCategory.ObjectType)
    assert_type(
        presentation.structure_sheaf.presheaf.section_ring(presentation.left_scheme_open),
        CategoryOfCategories.ElementType,
    )
    assert_type(
        presentation.structure_sheaf.presheaf.restriction(
            presentation.left_scheme_open, presentation.overlap_scheme_open
        ),
        MorphismCategory.ObjectType,
    )
    assert_type(presentation.overlap_swap, MorphismCategory.ObjectType)
    assert_type(presentation.base, SchemesCategory.ObjectType[AffineOpenCategory.ObjectType])
    assert_type(presentation.structure_map, SchemesCategory.MorphismType)
    assert_type(presentation.over_base, SliceLikeCategory.ObjectType)
    assert_type(presentation.swap_over_base, SliceLikeCategory.MorphismType)
