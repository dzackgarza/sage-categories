"""Static projection for finite scheme gluing and its universal mediator."""

from typing import assert_type

from sage_categories.cat.functors import NaturalTransformation
from sage_categories.geometry.affine import AffineSchemesCategory
from sage_categories.geometry.schemes import (
    AffineOpenChart,
    AffineOverlap,
    AffineOverlapPiece,
    FiniteAffineGluing,
    Schemes,
    SchemesCategory,
)


def check_scheme_general_gluing(
    charts: tuple[AffineSchemesCategory.ObjectType, ...],
    pieces: tuple[AffineOverlapPiece, ...],
    overlaps: tuple[AffineOverlap, ...],
    target: SchemesCategory.ObjectType,
    chart_maps: tuple[SchemesCategory.MorphismType, ...],
) -> None:
    schemes = Schemes()
    assert_type(schemes.affine_overlap(charts, 0, 1, pieces), AffineOverlap)
    glued = schemes.glue_affines(charts, overlaps)
    assert_type(glued, SchemesCategory.ObjectType)
    assert_type(glued.finite_affine_gluing(), FiniteAffineGluing)
    assert_type(glued.affine_cover(), tuple[AffineOpenChart, ...])
    assert_type(glued.local_affineness(), tuple[AffineOpenChart, ...])
    assert_type(
        glued.affine_cover()[0].structure_sheaf_comparison,
        NaturalTransformation,
    )
    assert_type(
        schemes.gluing_mediator(glued, target, chart_maps),
        SchemesCategory.MorphismType,
    )
