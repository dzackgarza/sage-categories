"""Contravariant Spec acts on prime points and global structure-sheaf sections."""

from sage_categories.algebra.commutative_rings import (
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
    prime_generators,
    quotient_ring,
)
from sage_categories.all import Mor, ask
from sage_categories.geometry.affine import AffineSchemes, Spec
from sage_categories.geometry.affine_global_sections import (
    GlobalSections,
    affine_global_sections_comparison,
    affine_structure_sheaf_global_map,
    global_sections,
    global_sections_map,
    global_sections_spec_comparison,
)


def test_spec_composes_on_prime_points_and_structure_sheaf_global_sections() -> None:
    field = prime_field(5)
    polynomial, (t,) = polynomial_ring(field, ("t",))
    square = presented_ring_homomorphism(polynomial, polynomial, (t * t,))
    shift = presented_ring_homomorphism(
        polynomial,
        polynomial,
        (t + polynomial.one(),),
    )
    scheme = Spec.on_object(polynomial)
    first = Spec.on_morphism(square.op())
    second = Spec.on_morphism(shift.op())
    composite = second * first

    assert first.domain() is scheme and first.codomain() is scheme
    assert second.domain() is scheme and second.codomain() is scheme
    assert global_sections(scheme) is polynomial
    assert GlobalSections.domain() is AffineSchemes().op()
    assert GlobalSections.codomain() is polynomial.category()

    # Sheaf action on the whole open is exactly the affine pullback and is
    # contravariant under scheme-map composition.
    assert affine_structure_sheaf_global_map(first) is first.pullback()
    assert global_sections_map(first) is first.pullback()
    assert global_sections_map(second) is second.pullback()
    assert (
        ask(
            global_sections_map(composite)
            == global_sections_map(first) * global_sections_map(second)
        )
        is True
    )

    # t |-> t^2 carries the prime t=2 to t=4.  Following by t |-> t+1
    # carries that point to t=0, and the direct composite has the same prime.
    two = polynomial.one() + polynomial.one()
    four = two + two
    affine = AffineSchemes()
    point = affine.spectrum_point(scheme, (t - two,))
    first_image, _first_stalk = affine.map_spectrum_point(first, point)
    first_generators = prime_generators(first_image.prime)
    assert len(first_generators) == 1
    assert ask(first_generators[0] == t - four) is True
    second_image, _second_stalk = affine.map_spectrum_point(second, first_image)
    composite_image, _composite_stalk = affine.map_spectrum_point(composite, point)
    second_generators = prime_generators(second_image.prime)
    composite_generators = prime_generators(composite_image.prime)
    assert len(second_generators) == 1 and len(composite_generators) == 1
    assert ask(second_generators[0] == t) is True
    assert ask(composite_generators[0] == t) is True

    # Both affine comparison transformations execute on objects and maps.
    ring_comparison = global_sections_spec_comparison.component(polynomial)
    assert (
        ring_comparison.domain() is polynomial
        and ring_comparison.codomain() is polynomial
    )
    assert (
        ask(ring_comparison == Mor(polynomial.category())(polynomial, polynomial).one())
        is True
    )
    affine_comparison = affine_global_sections_comparison.component(scheme)
    assert affine_comparison.codomain() is scheme
    assert affine_comparison.pullback().domain() is polynomial
    assert affine_comparison.pullback().codomain() is polynomial


def test_nilpotent_affine_scheme_keeps_its_global_section_and_prime_point() -> None:
    field = prime_field(5)
    polynomial, (epsilon_variable,) = polynomial_ring(field, ("e",))
    dual_numbers, projection = quotient_ring(
        polynomial,
        (epsilon_variable * epsilon_variable,),
    )
    epsilon = projection(epsilon_variable)
    dual_scheme = Spec.on_object(dual_numbers)
    field_scheme = Spec.on_object(field)

    assert dual_scheme is not field_scheme
    assert global_sections(dual_scheme) is dual_numbers
    assert global_sections(field_scheme) is field
    assert ask(epsilon == dual_numbers.zero()) is False
    assert ask(epsilon * epsilon == dual_numbers.zero()) is True

    # The unique expected prime of each zero-dimensional example is represented
    # directly; no point enumeration is required by the public affine owner.
    affine = AffineSchemes()
    dual_point = affine.spectrum_point(dual_scheme, (epsilon,))
    field_point = affine.spectrum_point(field_scheme, (field.zero(),))
    assert dual_point.scheme is dual_scheme and field_point.scheme is field_scheme
    assert ask(prime_generators(dual_point.prime)[0] == epsilon) is True
    assert ask(prime_generators(field_point.prime)[0] == field.zero()) is True


test_spec_composes_on_prime_points_and_structure_sheaf_global_sections()
test_nilpotent_affine_scheme_keeps_its_global_section_and_prime_point()
