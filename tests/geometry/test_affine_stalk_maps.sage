"""Affine spectrum points retain prime local rings and induced local maps."""

from sage_categories.algebra import polynomial_ring, presented_ring_homomorphism, prime_field
from sage_categories.geometry import AffineSchemes, Spec
from sage_categories.geometry.affine import native_affine_morphism, native_affine_scheme


def test_affine_map_retains_prime_image_and_stalk_map() -> None:
    field = prime_field(5)
    source_ring, (s,) = polynomial_ring(field, ("s",))
    target_ring, (t,) = polynomial_ring(field, ("t",))
    pullback = presented_ring_homomorphism(target_ring, source_ring, (s * s,))

    source = Spec.on_object(source_ring)
    target = Spec.on_object(target_ring)
    mapping = Spec.on_morphism(pullback.op())
    assert mapping.domain() is source and mapping.codomain() is target
    assert mapping.pullback() is pullback
    native_mapping = native_affine_morphism(mapping)
    assert native_mapping.value is mapping
    assert native_mapping.source is source
    assert native_mapping.target is target
    assert native_affine_scheme(source).construction.coordinate_ring is source_ring
    assert native_affine_scheme(target).construction.coordinate_ring is target_ring

    affine = AffineSchemes()
    point = affine.spectrum_point(source, (s,))
    image, stalk = affine.map_spectrum_point(mapping, point)

    assert image.scheme is target
    assert image.prime.ring is target_ring
    assert point.prime.ring is source_ring
    assert image.local_ring is stalk.domain()
    assert point.local_ring is stalk.codomain()
    assert image.localization.domain() is target_ring
    assert image.localization.codomain() is image.local_ring
    assert point.localization.domain() is source_ring
    assert point.localization.codomain() is point.local_ring


test_affine_map_retains_prime_image_and_stalk_map()
