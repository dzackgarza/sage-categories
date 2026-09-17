"""Affine spectra retain their prime-point topology and principal-open pullbacks."""

from sage_categories.algebra import (
    polynomial_ring,
    presented_ring_homomorphism,
    prime_field,
)
from sage_categories.algebra.commutative_rings import prime_generators
from sage_categories.all import ask
from sage_categories.geometry.affine import (
    AffineSchemes,
    Spec,
    affine_continuous_map,
    affine_open_preimage,
    affine_structure_sheaf,
    affine_topological_space,
)


def test_affine_map_acts_on_prime_points_and_principal_open_basis() -> None:
    field = prime_field(5)
    source_ring, (s,) = polynomial_ring(field, ("s",))
    target_ring, (t,) = polynomial_ring(field, ("t",))
    pullback = presented_ring_homomorphism(target_ring, source_ring, (s * s,))
    source = Spec.on_object(source_ring)
    target = Spec.on_object(target_ring)
    mapping = Spec.on_morphism(pullback.op())

    source_space = affine_topological_space(source)
    target_space = affine_topological_space(target)
    continuous = affine_continuous_map(mapping)
    assert continuous.domain() is source_space
    assert continuous.codomain() is target_space

    affine = AffineSchemes()
    source_point = affine.spectrum_point(source, (s,))
    represented_source_point = source_space.carrier().point(source_point)
    represented_target_point = continuous.underlying_map()(represented_source_point)
    target_point = represented_target_point.datum()
    direct_target_point, _ = affine.map_spectrum_point(mapping, source_point)
    assert target_point.scheme is target
    assert target_point.prime.ring is target_ring
    target_generators = prime_generators(target_point.prime)
    direct_generators = prime_generators(direct_target_point.prime)
    assert len(target_generators) == 1 and len(direct_generators) == 1
    assert ask(target_generators[0] == direct_generators[0]) is True

    source_opens, _source_sheaf = affine_structure_sheaf(source)
    target_opens, _target_sheaf = affine_structure_sheaf(target)
    source_root = source_opens.root()
    target_root = target_opens.root()
    target_principal = target_opens.principal_open(target_root, t)

    source_principal, section_pullback = affine_open_preimage(mapping, target_principal)
    assert source_principal.parent_open() is source_root
    source_localizing_element = source_principal.localizing_element()
    assert source_localizing_element is not None
    assert ask(source_localizing_element == s * s) is True
    assert section_pullback.domain() is target_principal.section_ring()
    assert section_pullback.codomain() is source_principal.section_ring()
    assert continuous.inverse_image().on_object(target_root) is source_root
    assert continuous.inverse_image().on_object(target_principal) is source_principal

    # Iterated principal opens are pulled back recursively, and the sheaf map is
    # the corresponding localization extension rather than a root-only shortcut.
    localized_t = target_principal.restriction_to(target_root)(t)
    target_second = target_opens.principal_open(target_principal, localized_t)
    source_second, second_pullback = affine_open_preimage(mapping, target_second)
    assert source_second.parent_open() is source_principal
    assert second_pullback.domain() is target_second.section_ring()
    assert second_pullback.codomain() is source_second.section_ring()
    assert continuous.inverse_image().on_object(target_second) is source_second


test_affine_map_acts_on_prime_points_and_principal_open_basis()
