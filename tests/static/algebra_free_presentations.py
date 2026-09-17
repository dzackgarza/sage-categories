"""Static projection for free and presented base-relative algebras."""

from collections.abc import Sequence
from typing import assert_type

from sage_categories.algebra.algebras import AlgebraCategory
from sage_categories.algebra.presented_algebras import (
    integer_free_algebra,
    integer_free_algebra_generator,
    integer_free_algebra_homomorphism,
    presented_algebra_diagram,
    presented_algebra_factor,
    presented_algebra_presentation,
    presented_algebra_projection,
    retain_split_algebra_presentation,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.cones import LimitConesCategory
from sage_categories.cat.functors import Functor


def algebra_presentation_types(
    algebras: AlgebraCategory,
    source: AlgebraCategory.ObjectType,
    quotient: AlgebraCategory.ObjectType,
    target: AlgebraCategory.ObjectType,
    first: AlgebraCategory.MorphismType,
    second: AlgebraCategory.MorphismType,
    projection: AlgebraCategory.MorphismType,
    section: AlgebraCategory.MorphismType,
    coequalizing: AlgebraCategory.MorphismType,
    images: Sequence[CategoryOfCategories.ElementType],
) -> None:
    assert_type(integer_free_algebra(algebras, ("x",)), AlgebraCategory.ObjectType)
    assert_type(
        integer_free_algebra_generator(algebras, source, 0),
        CategoryOfCategories.ElementType,
    )
    assert_type(
        integer_free_algebra_homomorphism(algebras, source, target, images),
        AlgebraCategory.MorphismType,
    )
    assert_type(
        retain_split_algebra_presentation(
            algebras,
            first,
            second,
            projection,
            section,
        ),
        AlgebraCategory.ObjectType,
    )
    assert_type(presented_algebra_diagram(algebras, quotient), Functor)
    assert_type(
        presented_algebra_presentation(algebras, quotient),
        LimitConesCategory.ObjectType,
    )
    assert_type(
        presented_algebra_projection(algebras, quotient),
        AlgebraCategory.MorphismType,
    )
    assert_type(
        presented_algebra_factor(algebras, quotient, target, coequalizing),
        AlgebraCategory.MorphismType,
    )
