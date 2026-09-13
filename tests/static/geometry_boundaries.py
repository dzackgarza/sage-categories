"""Static projection for the public affine and gluing boundaries."""

from typing import assert_type

from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry import (
    AffineOpenCategory,
    AffineSchemes,
    AffineSchemesCategory,
    ProjectiveLinePresentation,
    RingedSpacesCategory,
    RingPresheaf,
    RingSheaf,
    Schemes,
    SchemesCategory,
    TopologicalSpacesCategory,
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
        tuple[AffineOpenCategory, RingPresheaf[AffineOpenCategory.ObjectType]],
    )

    schemes = Schemes()
    assert_type(schemes, SchemesCategory)
    assert_type(schemes.affine(affine), SchemesCategory.ObjectType)
    assert_type(projective_line(ring), ProjectiveLinePresentation)


def check_represented_open_key_boundary(
    space: TopologicalSpacesCategory.ObjectType[tuple[str, int]],
    presheaf: RingPresheaf[tuple[str, int]],
    sheaf: RingSheaf[tuple[str, int]],
    source: RingedSpacesCategory.ObjectType[tuple[str, int]],
    target: RingedSpacesCategory.ObjectType[tuple[str, int]],
    continuous: MorphismCategory.ObjectType,
    open_object: CategoryOfCategories.ElementType,
    component: MorphismCategory.ObjectType,
    ringed: RingedSpacesCategory,
) -> None:
    key = ("stage", 37)

    def component_rule(open_key: tuple[str, int]) -> MorphismCategory.ObjectType:
        assert_type(open_key, tuple[str, int])
        return component

    assert_type(space.open_object(key), CategoryOfCategories.ElementType)
    assert_type(presheaf.open_key(open_object), tuple[str, int])
    assert_type(sheaf.presheaf.open_key(open_object), tuple[str, int])
    assert_type(source.space().open_object(key), CategoryOfCategories.ElementType)
    assert_type(
        ringed.homomorphism(source, target, continuous, component_rule),
        RingedSpacesCategory.MorphismType,
    )
