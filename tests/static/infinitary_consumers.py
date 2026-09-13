"""Static projection for the CP-infinity and adelic public consumers."""

from fractions import Fraction
from typing import assert_type

from sage_categories.algebra.adeles import (
    AdeleOpen,
    AdelePresentation,
    AdeleValue,
    adeles_of_rationals,
)
from sage_categories.algebra.local_fields import (
    ExactLocalFieldPresentation,
    ExactLocalValue,
    NoIntegralSubring,
    exact_padic_field,
    exact_rational_field,
    exact_real_field,
    prime_indices,
)
from sage_categories.cat.category import CategoryOfCategories
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.geometry.cw import (
    ComplexProjectivePoint,
    ProjectiveInfinityPresentation,
    ProjectiveSpacePresentation,
    complex_projective_point,
    projective_infinity,
    projective_space,
)
from sage_categories.geometry.spaces import TopologicalSpacesCategory
from sage_categories.geometry.topological_rings import (
    BinaryContinuity,
    ProductTopologyOpen,
    TopologicalRingsCategory,
)


def projective_types(presentation: ProjectiveInfinityPresentation) -> None:
    assert_type(projective_infinity(), ProjectiveInfinityPresentation)
    assert_type(projective_space(37), ProjectiveSpacePresentation)
    assert_type(presentation.finite_skeleton(37), ProjectiveSpacePresentation)
    assert_type(presentation.space.open_object(presentation.empty_open), CategoryOfCategories.ElementType)
    assert_type(presentation.structure_map(37), TopologicalSpacesCategory.MorphismType)
    assert_type(presentation.complex_conjugation(), TopologicalSpacesCategory.MorphismType)
    assert_type(complex_projective_point(1, 1j, 0), ComplexProjectivePoint)


def local_field_types(field: ExactLocalFieldPresentation) -> None:
    assert_type(exact_rational_field(), ExactLocalFieldPresentation)
    assert_type(exact_real_field(), ExactLocalFieldPresentation)
    assert_type(exact_padic_field(5), ExactLocalFieldPresentation)
    assert_type(prime_indices(), CategoryOfCategories.ElementType)
    assert_type(field.value(Fraction(1, 5)), CategoryOfCategories.ElementType)
    assert_type(ExactLocalValue.rational(5, Fraction(1, 5)), ExactLocalValue)
    assert_type(field.embed_rational(exact_rational_field().ring), MorphismCategory.ObjectType)
    assert_type(exact_rational_field().integers, CategoryOfCategories.ElementType | NoIntegralSubring)
    assert_type(exact_real_field().integers, CategoryOfCategories.ElementType | NoIntegralSubring)
    assert_type(exact_padic_field(5).integers, CategoryOfCategories.ElementType | NoIntegralSubring)


def adelic_types(
    presentation: AdelePresentation,
    value: AdeleValue,
    open_set: AdeleOpen,
) -> None:
    assert_type(adeles_of_rationals(), AdelePresentation)
    assert_type(presentation.ring, CategoryOfCategories.ElementType)
    assert_type(presentation.space, TopologicalSpacesCategory.ObjectType[AdeleOpen])
    assert_type(presentation.primes, CategoryOfCategories.ElementType)
    assert_type(presentation.topological_ring, TopologicalRingsCategory.ObjectType)
    assert_type(presentation.local_field(5), ExactLocalFieldPresentation)
    assert_type(presentation.point(value), CategoryOfCategories.ElementType)
    assert_type(presentation.diagonal_value(Fraction(1, 5)), AdeleValue)
    assert_type(presentation.component_map(5), MorphismCategory.ObjectType)
    assert_type(presentation.diagonal_map(), MorphismCategory.ObjectType)
    assert_type(presentation.open_object(open_set), CategoryOfCategories.ElementType)
    assert_type(presentation.topological_ring.addition_continuity(), BinaryContinuity)
    assert_type(presentation.topological_ring.multiplication_continuity(), BinaryContinuity)
    assert_type(
        presentation.topological_ring.addition_preimage(presentation.open_object(open_set)),
        ProductTopologyOpen,
    )
    assert_type(
        presentation.topological_ring.multiplication_preimage(presentation.open_object(open_set)),
        ProductTopologyOpen,
    )
