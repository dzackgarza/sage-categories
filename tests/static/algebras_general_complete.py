"""Static terminal surface for base-relative algebras."""

from collections.abc import Sequence
from typing import assert_type

from sage_categories.algebra.algebra_objects import (
    AlgebraCategory,
    Algebras,
    integer_free_algebra,
    integer_free_algebra_generator,
    integer_free_algebra_homomorphism,
    presented_algebra_factor,
    presented_algebra_projection,
    restrict_algebra_scalars,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.functors import Functor
from sage_categories.cat.monoidal import MonoidalStructuresCategory
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.structured_objects import MonoidCategory


def complete_algebra_types(
    source: AlgebraCategory,
    target: AlgebraCategory,
    base: MonoidCategory.ObjectType,
    monoidal: MonoidalStructuresCategory.ObjectType,
    scalar_map: MorphismCategory.ObjectType,
    free: AlgebraCategory.ObjectType,
    quotient: AlgebraCategory.ObjectType,
    target_object: AlgebraCategory.ObjectType,
    coequalizing: AlgebraCategory.MorphismType,
    images: Sequence[CategoryOfCategories.ElementType],
) -> None:
    assert_type(Algebras(base, monoidal), AlgebraCategory)
    assert_type(source.base(), MonoidCategory.ObjectType)
    assert_type(source.monoid_presentation(), Functor)
    assert_type(source.to_modules(), Functor)
    assert_type(source.U_R(), Functor)
    assert_type(source.to_sets(), Functor)
    assert_type(restrict_algebra_scalars(source, target, scalar_map), Functor)
    assert_type(integer_free_algebra(source, ("x", "y")), AlgebraCategory.ObjectType)
    assert_type(
        integer_free_algebra_generator(source, free, 0),
        CategoryOfCategories.ElementType,
    )
    assert_type(
        integer_free_algebra_homomorphism(source, free, target_object, images),
        AlgebraCategory.MorphismType,
    )
    assert_type(
        presented_algebra_projection(source, quotient),
        AlgebraCategory.MorphismType,
    )
    assert_type(
        presented_algebra_factor(source, quotient, target_object, coequalizing),
        AlgebraCategory.MorphismType,
    )
