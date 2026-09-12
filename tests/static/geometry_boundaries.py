"""Static projection for the public affine and gluing boundaries."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry import (
    AffineOpenCategory,
    AffineSchemes,
    AffineSchemesCategory,
    ProjectiveLinePresentation,
    RingPresheaf,
    Schemes,
    SchemesCategory,
    affine_structure_sheaf,
    projective_line,
)


def check_affine_boundary(
    affine: AffineSchemesCategory.ObjectType,
    ring: CategoryOfCategories.ElementType,
    arrow: AffineSchemesCategory.MorphismType,
) -> None:
    assert_type(AffineSchemes(), AffineSchemesCategory)
    assert_type(affine.coordinate_ring(), CategoryOfCategories.ElementType)
    assert_type(arrow.domain(), AffineSchemesCategory.ObjectType)
    assert_type(arrow.codomain(), AffineSchemesCategory.ObjectType)
    assert_type(arrow.pullback(), MorphismCategory.ObjectType)
    assert_type(
        affine_structure_sheaf(affine),
        tuple[AffineOpenCategory, RingPresheaf],
    )

    schemes = Schemes()
    assert_type(schemes, SchemesCategory)
    assert_type(schemes.affine(affine), SchemesCategory.ObjectType)
    assert_type(projective_line(ring), ProjectiveLinePresentation)
