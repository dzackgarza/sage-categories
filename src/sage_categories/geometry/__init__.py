"""Topological, ringed, and scheme-theoretic leaves."""

from sage_categories.geometry.affine import (
    AffineOpen,
    AffineOpenCategory,
    AffineSchemes,
    AffineSchemesCategory,
    AffineSpectrumPoint,
    Spec,
    affine_structure_sheaf,
)
from sage_categories.geometry.cw import (
    ComplexProjectivePoint,
    CWOpen,
    ProjectiveInfinityPresentation,
    ProjectiveSpacePresentation,
    complex_projective_point,
    projective_infinity,
    projective_space,
)
from sage_categories.geometry.ringed_spaces import RingedSpaces, RingedSpacesCategory
from sage_categories.geometry.schemes import (
    ProjectiveLinePresentation,
    Schemes,
    SchemesCategory,
    TwoChartGluing,
    projective_line,
)
from sage_categories.geometry.sheaves import (
    RingPresheaf,
    RingSheaf,
    ring_presheaf,
    ring_presheaf_from_functor,
    ring_sheaf,
)
from sage_categories.geometry.spaces import TopologicalSpaces, TopologicalSpacesCategory
from sage_categories.geometry.topological_rings import (
    TopologicalRings,
    TopologicalRingsCategory,
)

__all__ = [
    "AffineOpen",
    "AffineOpenCategory",
    "AffineSchemes",
    "AffineSchemesCategory",
    "AffineSpectrumPoint",
    "CWOpen",
    "ComplexProjectivePoint",
    "ProjectiveInfinityPresentation",
    "ProjectiveLinePresentation",
    "ProjectiveSpacePresentation",
    "RingPresheaf",
    "RingSheaf",
    "RingedSpaces",
    "RingedSpacesCategory",
    "Schemes",
    "SchemesCategory",
    "Spec",
    "TopologicalRings",
    "TopologicalRingsCategory",
    "TopologicalSpaces",
    "TopologicalSpacesCategory",
    "TwoChartGluing",
    "affine_structure_sheaf",
    "complex_projective_point",
    "projective_infinity",
    "projective_line",
    "projective_space",
    "ring_presheaf",
    "ring_presheaf_from_functor",
    "ring_sheaf",
]
